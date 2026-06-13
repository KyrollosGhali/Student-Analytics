import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import get_master, load_engagement

st.title("14. At-Risk Student Ranking")
st.markdown("**Business Question:** Combine low attendance, declining engagement, and failed key concepts into a risk ranking.")
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
engagement = load_engagement().copy()

engagement = engagement.dropna(subset=["event_datetime"])
max_date = engagement["event_datetime"].max()
recent_cutoff = max_date - pd.Timedelta(days=30)

recent = engagement[engagement["event_datetime"] >= recent_cutoff].groupby("student_id").size()
prior = engagement[engagement["event_datetime"] < recent_cutoff].groupby("student_id").size()

master["engagement_trend"] = (
    recent.reindex(master["student_id"], fill_value=0).values
    - prior.reindex(master["student_id"], fill_value=0).values
)

def normalize(series):
    return 1 - ((series - series.min()) / (series.max() - series.min() + 1e-9))

master["risk_score"] = (
    normalize(master["attendance_rate"]) * 0.30
    + normalize(master["avg_grade"]) * 0.30
    + normalize(master["engagement_trend"]) * 0.20
    + (master["failed_concepts_count"] / (master["failed_concepts_count"].max() + 1e-9)) * 0.20
)

top10 = master.sort_values("risk_score", ascending=False).head(10)

fig = px.bar(
    top10.sort_values("risk_score"),
    x="risk_score",
    y="full_name",
    color="risk_score",
    orientation="h",
    color_continuous_scale="Reds",
    title="Top 10 Students Requiring Intervention",
    labels={"risk_score": "Risk Score", "full_name": "Student"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Insight")
st.write(
    f"The highest-risk student is **{top10.iloc[0]['full_name']}** in **{top10.iloc[0]['group_id']}** "
    f"with a risk score of **{top10.iloc[0]['risk_score']:.3f}**. "
    "The list is concentrated in a small number of groups, which suggests a cohort-level issue rather than isolated underperformance."
)

# st.dataframe(
#     top10[[
#         "student_id",
#         "full_name",
#         "group_id",
#         "attendance_rate",
#         "avg_grade",
#         "engagement_trend",
#         "failed_concepts_count",
#         "risk_score",
#     ]].rename(
#         columns={
#             "student_id": "Student ID",
#             "full_name": "Student",
#             "group_id": "Group ID",
#             "attendance_rate": "Attendance Rate",
#             "avg_grade": "Average Grade",
#             "engagement_trend": "Engagement Trend",
#             "failed_concepts_count": "Failed Concepts",
#             "risk_score": "Risk Score",
#         }
#     )
# )

st.caption("Method: combine low attendance, declining engagement, low grade, and failed concepts into a weighted risk score.")
