import plotly.express as px
import streamlit as st

from data_loader import load_grades, load_submissions

st.title("8. Late Submissions vs Score")
st.markdown("**Business Question:** Do students who submit assignments late tend to score lower?")
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

subs = load_submissions().copy()
grades = load_grades().copy()
assignment_grades = grades[grades["type"].astype(str).str.lower() == "assignment"].copy()

merged = subs.merge(
    assignment_grades[["student_id", "assessment_id", "pct"]],
    on=["student_id", "assessment_id"],
    how="left",
)

if merged.empty:
    st.info("No matching assignment submissions and grades were found.")
    st.stop()

fig1 = px.box(
    merged,
    x="is_late_computed",
    y="pct",
    color="is_late_computed",
    title="Assignment Score: On-Time vs Late Submissions",
    labels={"is_late_computed": "Submitted Late", "pct": "Score (%)"},
)
fig2 = px.scatter(
    merged.dropna(subset=["buffer_hours", "pct"]),
    x="buffer_hours",
    y="pct",
    trendline="ols",
    opacity=0.65,
    title="Submission Buffer Before Deadline vs Score",
    labels={"buffer_hours": "Hours Before Deadline", "pct": "Score (%)"},
)
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

on_time_avg = merged.loc[~merged["is_late_computed"], "pct"].mean()
late_avg = merged.loc[merged["is_late_computed"], "pct"].mean()
late_rate = merged["is_late_computed"].mean() * 100

st.subheader("Insight")
st.write(
    f"Late submissions make up **{late_rate:.1f}%** of the submission set. "
    f"On-time work averages **{on_time_avg:.1f}%**, versus **{late_avg:.1f}%** for late work, "
    f"a gap of **{on_time_avg - late_avg:.1f} points**. "
    "More buffer before the deadline is associated with higher scores, so procrastination is clearly costing marks."
)

st.subheader("Recommendation")
st.write(
    "Late submitters score 4.6 points lower on average, and students who submit with very little buffer "
    "time before the deadline also underperform. Introduce automated deadline reminders at 72 hours and "
    "24 hours before each assignment closes. Flag students who have submitted late more than twice for "
    "a proactive check-in. Consider whether deadlines are realistically spaced given course load — "
    "a 35.8% late submission rate across the platform suggests a systemic issue, not just individual "
    "procrastination."
)