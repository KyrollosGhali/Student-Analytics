import plotly.express as px
import streamlit as st

from data_loader import get_master , load_courses , load_groups

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
# filter out courses with fewer than 2 students to avoid misleading stats
courses = load_courses().copy()
course_counts = master["course_id"].value_counts()
valid_courses = course_counts[course_counts >= 2].index.tolist()
master = master[master["course_id"].isin(valid_courses)]
column1 , column2 , column3 = st.columns([1, 1, 2])
with column1:
    st.metric("Total Courses", master["course_id"].nunique())
    courses_options = sorted(master["course_id"].unique())
    selected_course = st.multiselect("Filter by Course", options=courses_options)
    master = master[master["course_id"].isin(selected_course)] if selected_course else master
with column2:
    st.metric("Total Students", master["student_id"].nunique())
    groups = load_groups().copy()
    group_options = sorted(groups["group_id"].unique())
    selected_group = st.multiselect("Filter by Group", options=group_options)
    if "All groups" not in selected_group:
        master = master[master["group_id"].isin(selected_group)]
course_stats = (
    master.groupby("course_id")["avg_grade"]
    .agg(mean="mean", std="std", count="count")
    .reset_index()
    .sort_values("mean", ascending=False)
)
filter_courses = course_stats["course_id"].tolist()
course_stats["course_id"] = course_stats["course_id"].astype(str)
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

st.subheader("Recommendation")
st.write(
    "C005 is the weakest course by average grade (59.7%) with a meaningful cohort size (n=46), making it "
    "the top priority for curriculum review. Audit the course content, assessment difficulty, and instructor "
    "delivery. C001 is the benchmark to learn from — study what makes it the strongest performer and apply "
    "those patterns to C005. Treat C007 as a non-comparable outlier (1 student only) until more students enroll."
)