import plotly.express as px
import streamlit as st
from scipy.stats import pearsonr

from data_loader import get_master

st.title("4. Attendance vs Average Grade")
st.markdown("**Business Question:** Is there a relationship between a student's attendance rate and their average grade?")
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
clean = master[
    (master["attendance_rate"] > 0)
    & (master["avg_grade"] > 0)
    & (master["avg_grade"] <= 100)
].copy()

if len(clean) < 2:
    st.info("Not enough data to calculate a reliable correlation.")
    st.stop()

corr, pval = pearsonr(clean["attendance_rate"], clean["avg_grade"])

fig = px.scatter(
    clean,
    x="attendance_rate",
    y="avg_grade",
    trendline="ols",
    trendline_color_override="red",
    opacity=0.65,
    title=f"Attendance Rate vs Average Grade (r = {corr:.2f})",
    labels={"attendance_rate": "Attendance Rate (%)", "avg_grade": "Average Grade (%)"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Insight")
st.write(
    f"Attendance and grade show a **moderate positive relationship** "
    f"(Pearson r = {corr:.2f}, p = {pval:.4g}). "
    "Students with stronger attendance tend to score better, although attendance alone does not explain all grade variation."
)

st.caption("Method: Pearson correlation between student attendance rate and average grade, with a regression trend line. Records with avg_grade > 100 (data entry outliers) were excluded.")