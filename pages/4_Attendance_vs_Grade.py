import base64
from pathlib import Path

import plotly.express as px
import streamlit as st
from scipy.stats import pearsonr

from data_loader import get_master, load_grades, load_groups

st.title("4. Attendance vs Average Grade")
st.markdown("**Business Question:** Is there a relationship between a student's attendance rate and their average grade?")

# ---------- Logo ----------
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

# ---------- Load data ----------
master = get_master().copy()
grades = load_grades().copy()

if "pct" not in grades.columns:
    grades["pct"] = grades["score"] / grades["max_score"] * 100

grades = grades[grades["pct"] <= 100]

# ---------- Filters ----------
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    assessment_types =  sorted(grades["type"].dropna().unique().tolist())
    selected_type = st.multiselect("Filter by Assessment Type", options=assessment_types)

with col_f2:
    groups = load_groups()
    group_options = sorted(groups["group_id"].dropna().unique().tolist())
    selected_group = st.multiselect("Filter by Group", options=group_options)

# ---------- Apply assessment type filter to recompute avg_grade ----------
if selected_type:
    filtered_grades = grades[grades["type"].isin(selected_type)]
else:
    filtered_grades = grades.copy()

avg_grade_filtered = (
    filtered_grades.groupby("student_id")["pct"]
    .mean()
    .reset_index()
    .rename(columns={"pct": "avg_grade_filtered"})
)

# merge filtered avg grade back into master
master = master.merge(avg_grade_filtered, on="student_id", how="left")

# ---------- Apply group filter ----------
if selected_group:
    master = master[master["group_id"].isin(selected_group)]

# ---------- Apply student filter ----------
# if selected_students:
#     master = master[master["full_name"].isin(selected_students)]

# ---------- Metrics ----------
col_m1, col_m2 = st.columns(2)
col_m1.metric("Total Students", master["student_id"].nunique())
col_m2.metric(
    "Students with Attendance & Grade Data",
    master.dropna(subset=["attendance_rate", "avg_grade_filtered"])["student_id"].nunique(),
)

# ---------- Clean for correlation ----------
clean = master[
    (master["attendance_rate"] > 0)
    & (master["avg_grade_filtered"] > 0)
    & (master["avg_grade_filtered"] <= 100)
].dropna(subset=["attendance_rate", "avg_grade_filtered"]).copy()

if len(clean) < 2:
    st.info("Not enough data to calculate a reliable correlation.")
    st.stop()

corr, pval = pearsonr(clean["attendance_rate"], clean["avg_grade_filtered"])

# ---------- Chart ----------
type_label = ", ".join(selected_type) if selected_type else "All Assessment Types"

fig = px.scatter(
    clean,
    x="attendance_rate",
    y="avg_grade_filtered",
    trendline="ols",
    trendline_color_override="red",
    hover_data=["full_name"],
    opacity=0.65,
    title=f"Attendance Rate vs Average Grade — {type_label} (r = {corr:.2f})",
    labels={
        "attendance_rate": "Attendance Rate (%)",
        "avg_grade_filtered": "Average Grade (%)",
    },
)
st.plotly_chart(fig, use_container_width=True)

# ---------- Insight ----------
st.subheader("Insight")
strength = "strong" if abs(corr) > 0.6 else "moderate" if abs(corr) > 0.3 else "weak"
direction = "positive" if corr > 0 else "negative"
st.write(
    f"For **{type_label}**, attendance and grade show a **{strength} {direction} relationship** "
    f"(Pearson r = {corr:.2f}, p = {pval:.4g}). "
    "Students with stronger attendance tend to score better, although attendance alone does not explain all grade variation."
)

st.caption(
    "Method: Pearson correlation between student attendance rate and average grade per selected assessment type, "
    "with a regression trend line. Records with avg_grade > 100 were excluded."
)
st.subheader("Recommendation")
st.write(
    "The moderate positive correlation (r = 0.42) confirms that attendance is a meaningful lever for grade "
    "improvement, but not the only one. Prioritize attendance interventions for students who are already "
    "showing weak grades — for them, improving attendance is the lowest-effort highest-return action. "
    "Do not rely on attendance alone as a performance predictor; combine it with engagement and concept "
    "mastery signals for a more complete picture."
)