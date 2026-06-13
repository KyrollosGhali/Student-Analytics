import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from data_loader import get_master

st.title("11. Student Segmentation")
st.markdown("**Business Question:** Build a student segmentation using attendance, engagement, average grade, and number of failed concepts.")
from pathlib import Path
import base64
logo_path = Path("./images/logo.png")
if logo_path.exists():
    logo_base64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <style>
        .fixed-logo {{
            position: fixed;
            top: 3.8rem;
            right: 1rem;
            z-index: 999;
            background: rgba(255, 255, 255, 0);
            border-radius: 12px;
            padding: 8px 10px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
        }}
        .fixed-logo img {{
            width: 300px;
            height: auto;
            display: block;
        }}
        @media (max-width: 768px) {{
            .fixed-logo {{
                top: 4.2rem;
                right: 0.5rem;
                padding: 6px 8px;
            }}
            .fixed-logo img {{
                width: 110px;
            }}
        }}
        </style>
        <div class="fixed-logo">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" />
        </div>
        """,
        unsafe_allow_html=True,
    )

master = get_master().copy()
master["video_hours"] = master["total_video_seconds"] / 3600
features = ["attendance_rate", "engagement_count", "video_hours", "avg_grade", "failed_concepts_count"]
X = master[features].fillna(0)
scaled = StandardScaler().fit_transform(X)
coords = PCA(n_components=2, random_state=42).fit_transform(scaled)
master["pca_1"] = coords[:, 0]
master["pca_2"] = coords[:, 1]

n_clusters = st.slider("Number of segments", 2, 6, 4)
model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
master["segment"] = model.fit_predict(scaled).astype(str)

fig = px.scatter(
    master,
    x="pca_1",
    y="pca_2",
    color="segment",
    hover_data=["full_name", "attendance_rate", "avg_grade", "failed_concepts_count"],
    title="Student Segments in PCA Space",
    labels={"pca_1": "PCA Component 1", "pca_2": "PCA Component 2"},
)
st.plotly_chart(fig, use_container_width=True)

profile = master.groupby("segment")[features].mean().round(1)
# st.subheader("Segment Profiles")
# st.dataframe(
#     profile.rename(
#         columns={
#             "attendance_rate": "Attendance Rate",
#             "engagement_count": "Engagement Events",
#             "video_hours": "Video Hours",
#             "avg_grade": "Average Grade",
#             "failed_concepts_count": "Failed Concepts",
#         }
#     )
# )

overall = profile.mean()
labels = []
for seg, row in profile.iterrows():
    if row["avg_grade"] >= overall["avg_grade"] and row["attendance_rate"] >= overall["attendance_rate"]:
        labels.append(f"Segment {seg}: high-achieving, well-attended cohort.")
    elif row["avg_grade"] < overall["avg_grade"] and row["attendance_rate"] < overall["attendance_rate"]:
        labels.append(f"Segment {seg}: at-risk cohort with weak attendance and lower grades.")
    elif row["avg_grade"] >= overall["avg_grade"] and row["engagement_count"] < overall["engagement_count"]:
        labels.append(f"Segment {seg}: quiet achievers with decent grades but lower activity.")
    else:
        labels.append(f"Segment {seg}: mixed or transitional cohort.")

st.subheader("Insight")
for label in labels:
    st.write(label)

st.caption("Method: standardize key learning signals, cluster with KMeans, and visualize the segments with PCA.")
