import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_grades, load_groups, load_students

st.title("15. Group Grade Trends")
st.markdown("**Business Question:** Track each group's average grade across successive assessments.")
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

grades = load_grades().copy()
students = load_students().copy()
groups = load_groups().copy()

if "group_id" not in grades.columns:
    grades = grades.merge(students[["student_id", "group_id"]], on="student_id", how="left")

trend = (
    grades.groupby(["group_id", "assessment_id", "date"], as_index=False)["pct"]
    .mean()
    .sort_values(["group_id", "date"])
)
trend["assessment_order"] = trend.groupby("group_id").cumcount() + 1

fig = px.line(
    trend,
    x="assessment_order",
    y="pct",
    color="group_id",
    markers=True,
    title="Group Average Grade Across Successive Assessments",
    labels={"assessment_order": "Assessment Sequence", "pct": "Average Grade (%)"},
)
st.plotly_chart(fig, use_container_width=True)

slopes = {}
for group_id, sub in trend.groupby("group_id"):
    if len(sub) > 1:
        slopes[group_id] = np.polyfit(sub["assessment_order"], sub["pct"], 1)[0]

if not slopes:
    st.info("Not enough group-level grade history to estimate trends yet.")
    st.stop()

slope_df = pd.DataFrame(
    [{"group_id": g, "slope": s} for g, s in slopes.items()]
).merge(groups[["group_id", "group_name"]], on="group_id", how="left").sort_values("slope", ascending=False)

def trend_label(value):
    if value > 0.5:
        return "improving"
    if value < -0.5:
        return "declining"
    return "stable"

st.subheader("Insight")
st.write(
    f"The best-trending group is **{slope_df.iloc[0]['group_name']}** and the weakest trend is "
    f"**{slope_df.iloc[-1]['group_name']}**. "
    f"Most cohorts are **{trend_label(slope_df['slope'].median())}**, with the steepest decline in "
    f"**{slope_df.iloc[-1]['group_id']}** at {slope_df.iloc[-1]['slope']:.3f} points per assessment."
)

# st.dataframe(slope_df.rename(columns={"group_id": "Group ID", "group_name": "Group", "slope": "Trend Slope"}))

st.caption("Method: average grades by group and assessment order, then estimate a linear slope per group.")
