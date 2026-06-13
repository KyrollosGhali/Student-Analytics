import plotly.express as px
import streamlit as st

from data_loader import get_master

st.title("3. Course Performance Comparison")
st.markdown("**Business Question:** Which course has the highest and lowest average grade, and how does grade spread differ between them?")
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
course_stats = (
    master.groupby("course_id")["avg_grade"]
    .agg(mean="mean", std="std", count="count")
    .reset_index()
    .sort_values("mean", ascending=False)
)

fig1 = px.bar(
    course_stats,
    x="course_id",
    y="mean",
    error_y="std",
    color="mean",
    color_continuous_scale="Viridis",
    title="Average Grade by Course",
    labels={"course_id": "Course", "mean": "Average Grade (%)"},
)
fig2 = px.box(
    master,
    x="course_id",
    y="avg_grade",
    points="all",
    title="Grade Spread by Course",
    labels={"course_id": "Course", "avg_grade": "Average Grade (%)"},
)
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

best = course_stats.iloc[0]
worst = course_stats[course_stats["count"] >= 2].iloc[-1] if (course_stats["count"] >= 2).any() else course_stats.iloc[-1]

st.subheader("Insight")
st.write(
    f"Among meaningful cohort sizes, **{best['course_id']}** leads with a mean grade of "
    f"**{best['mean']:.1f}%**. **{worst['course_id']}** is the weakest course at "
    f"**{worst['mean']:.1f}%**, and its spread is {worst['std']:.1f} points. "
    f"The gap suggests that course-level difficulty and consistency differ materially across the platform."
)

# st.dataframe(course_stats.rename(columns={"course_id": "Course", "mean": "Average Grade", "std": "Std Dev", "count": "Student Count"}))
