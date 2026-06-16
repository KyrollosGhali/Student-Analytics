import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.cluster import KMeans
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
feature_labels = {
    "attendance_rate": "Attendance Rate",
    "engagement_count": "Engagement Events",
    "video_hours": "Video Hours",
    "avg_grade": "Average Grade",
    "failed_concepts_count": "Failed Concepts",
}

X = master[features].fillna(0)
scaled = StandardScaler().fit_transform(X)

n_clusters = st.slider("Number of segments", 2, 6, 4)
model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
master["segment"] = model.fit_predict(scaled).astype(str)

# --- Segment sizes ---
seg_counts = master["segment"].value_counts().sort_index().reset_index()
seg_counts.columns = ["segment", "count"]

# --- Segment profiles (mean of each feature per segment) ---
profile = master.groupby("segment")[features].mean().round(1)
overall = profile.mean()

# --- Normalized profile for radar charts ---
norm_profile = (profile - X.min()) / (X.max() - X.min() + 1e-9)
norm_profile = norm_profile.clip(0, 1)

# --- Radar chart: one subplot per segment to avoid overlap ---
categories = [feature_labels[f] for f in features]

n_segs = len(profile)
cols = min(n_segs, 3)
rows = (n_segs + cols - 1) // cols

specs = [[{"type": "polar"} for _ in range(cols)] for _ in range(rows)]

fig_radar = make_subplots(
    rows=rows, cols=cols,
    specs=specs,
    subplot_titles=[f"Segment {seg}" for seg in profile.index],
)

color_seq = px.colors.qualitative.Plotly

for i, (seg, row) in enumerate(norm_profile.iterrows()):
    r, c = divmod(i, cols)
    values = row.tolist()
    values.append(values[0])
    cats = categories + [categories[0]]

    fig_radar.add_trace(
        go.Scatterpolar(
            r=values,
            theta=cats,
            fill="toself",
            name=f"\u2003\u2003Segment {seg}        ",
            line_color=color_seq[i % len(color_seq)],
            showlegend=False,
            
        ),
        row=r + 1, col=c + 1,
    )

fig_radar.update_layout(
    title="Segment Profiles (normalized 0-1)",
    height=300 * rows,
)

# apply consistent radial range to every polar subplot
polar_keys = [k for k in fig_radar.layout if k.startswith("polar")]
for k in polar_keys:
    fig_radar.layout[k].radialaxis.range = [0, 1]
    fig_radar.layout[k].radialaxis.visible = True

st.plotly_chart(fig_radar, use_container_width=True)

# --- Scatter on two interpretable axes: attendance vs grade, sized by failed concepts ---

fig_scatter = px.scatter(
    master,
    x="attendance_rate",
    y="avg_grade",
    color="segment",
    size="failed_concepts_count",
    hover_data=["full_name", "engagement_count", "video_hours", "failed_concepts_count"],
    title="Segments: Attendance vs Average Grade (bubble size = failed concepts)",
    labels={"attendance_rate": "Attendance Rate (%)", "avg_grade": "Average Grade (%)"},
)
# --- Grouped bar chart: average metrics per segment ---
bar_metrics = ["attendance_rate", "avg_grade", "failed_concepts_count"]
bar_labels = {
    "attendance_rate": "Attendance Rate (%)",
    "avg_grade": "Average Grade (%)",
    "failed_concepts_count": "Failed Concepts",
}

bar_df = profile[bar_metrics].reset_index().melt(
    id_vars="segment", var_name="metric", value_name="value"
)
bar_df["metric"] = bar_df["metric"].map(bar_labels)

fig_bars = px.bar(
    bar_df,
    x="segment",
    y="value",
    color="metric",
    barmode="group",
    text="value",
    title="Average Attendance, Grade, and Failed Concepts per Segment",
    labels={"segment": "Segment", "value": "Value"},
)
fig_bars.update_traces(textposition="outside")
st.plotly_chart(fig_bars, use_container_width=True)
# --- Segment size bar chart ---
fig_size = px.bar(
    seg_counts,
    x="segment",
    y="count",
    title="Number of Students per Segment",
    labels={"segment": "Segment", "count": "Students"},
    text="count",
)
fig_size.update_traces(textposition="outside")
st.plotly_chart(fig_size, use_container_width=True)

# --- Auto-generated insight labels ---
labels = []
for seg, row in profile.iterrows():
    n = int(seg_counts.loc[seg_counts["segment"] == seg, "count"].values[0])
    if row["avg_grade"] >= overall["avg_grade"] and row["attendance_rate"] >= overall["attendance_rate"]:
        labels.append(f"Segment {seg} ({n} students): high-achieving, well-attended cohort.")
    elif row["avg_grade"] < overall["avg_grade"] and row["attendance_rate"] < overall["attendance_rate"]:
        labels.append(f"Segment {seg} ({n} students): at-risk cohort with weak attendance and lower grades.")
    elif row["avg_grade"] >= overall["avg_grade"] and row["engagement_count"] < overall["engagement_count"]:
        labels.append(f"Segment {seg} ({n} students): quiet achievers with decent grades but lower activity.")
    else:
        labels.append(f"Segment {seg} ({n} students): mixed or transitional cohort.")

st.subheader("Insight")
for label in labels:
    st.write(label)
st.subheader("Recommendation")
st.write(
    "Segment 1 (64 students) is the clear at-risk group: low attendance, low grades, low engagement, "
    "and an average of 12 failed concepts. These students need immediate and structured intervention — "
    "personal outreach from instructors, mandatory catch-up sessions, and a simplified study plan. "
    "Segment 2 (125 students) needs academic support despite moderate attendance — tutoring or concept "
    "revision sessions would help. Segments 0 and 3 are performing well and require only light-touch "
    "monitoring. Use this segmentation monthly as an early-warning dashboard, not a one-time snapshot."
)