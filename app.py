import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path
import base64
st.set_page_config(page_title="Kayfa Platform Analytics", layout="wide")

logo_path = Path("images/logo.png")
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
            width: 240px;
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
from data_loader import get_master, load_courses, load_groups, load_students, load_attendance

st.set_page_config(page_title="Kayfa Platform Analytics", layout="wide", page_icon="📊")

st.title("Kayfa Platform — Student Analytics Dashboard - Task Week2")

st.markdown(
    """
Welcome to the Kayfa analytics suite. Use the sidebar to move through the 15 business questions
covering attendance, performance, engagement, concept mastery, student risk, and group health.
All figures below are reconciled live from MongoDB Atlas.
"""
)

# ---------- Summary metrics ----------
master = get_master()
courses = load_courses()
groups = load_groups()
students = load_students()
attendance = load_attendance()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Courses", len(courses))
col2.metric("Groups", len(groups))
col3.metric("Students", len(students))
col4.metric("Avg Attendance", f"{master['attendance_rate'].mean():.1f}%")
col5.metric("Avg Grade", f"{master['avg_grade'].mean():.1f}%")

st.divider()

# ---------- Appearance charts ----------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    course_counts = students.merge(groups[["group_id", "course_id"]], on="group_id", how="left")
    course_counts = course_counts.merge(courses[["course_id", "course_name"]], on="course_id", how="left")
    course_counts = course_counts.groupby("course_name").size().reset_index(name="student_count")

    fig1 = px.pie(
        course_counts, names="course_name", values="student_count",
        title="Student Distribution by Course", hole=0.4
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    grade_dist = master[master["avg_grade"] > 0]
    fig2 = px.histogram(
        grade_dist, x="avg_grade", nbins=20,
        title="Distribution of Average Grades",
        labels={"avg_grade": "Average Grade (%)"}
    )
    st.plotly_chart(fig2, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    attendance["week"] = attendance["session_datetime"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_att = attendance.groupby("week")["status"].apply(
        lambda s: (s == "attended").mean() * 100
    ).reset_index(name="attendance_rate")

    fig3 = px.area(
        weekly_att, x="week", y="attendance_rate",
        title="Platform-wide Weekly Attendance Trend",
        labels={"week": "Week", "attendance_rate": "Attendance Rate (%)"}
    )
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    age_groups = pd.cut(
        master["age"], bins=[17, 22, 27, 32, 37, 100],
        labels=["18-22", "23-27", "28-32", "33-37", "38+"]
    )
    age_counts = age_groups.value_counts().sort_index().reset_index()
    age_counts.columns = ["age_band", "count"]

    fig4 = px.bar(
        age_counts, x="age_band", y="count",
        title="Student Count by Age Band",
        labels={"age_band": "Age Band", "count": "Students"}
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---------- Navigation cards ----------
st.subheader("Explore the analysis")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    st.markdown("**📅 Attendance & Engagement**")
    st.caption("Pages 1, 9, 10 — who's showing up and when activity dips.")

with nav_col2:
    st.markdown("**📈 Performance**")
    st.caption("Pages 2, 3, 4, 5, 8 — scores, courses, and what drives grades.")

with nav_col3:
    st.markdown("**💡 Concept Mastery**")
    st.caption("Pages 6, 7 — curriculum weak spots and trends over time.")

with nav_col4:
    st.markdown("**👥 Groups & Segments**")
    st.caption("Pages 11, 12, 13, 15 — segmentation, sizing, and merges.")

st.info("⚠️ **Priority — Page 14**: At-risk student ranking. Top 10 students an instructor should contact first.")

st.caption("Data cached for 10 minutes. Use the refresh button on individual pages if data was just updated.")