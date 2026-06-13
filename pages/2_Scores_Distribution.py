import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_grades

st.title("2. Score Distribution by Assessment Type")
st.markdown("**Business Question:** How are scores distributed by assessment type across the platform, and where is performance most volatile?")
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
if grades.empty:
    st.info("No grade data available yet.")
    st.stop()

if "pct" not in grades.columns:
    grades["pct"] = grades["score"] / grades["max_score"] * 100

def remove_outliers(group):
    q1 = group["pct"].quantile(0.25)
    q3 = group["pct"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return group[(group["pct"] >= lower_bound) & (group["pct"] <= upper_bound)]
grades = grades.groupby("type").apply(remove_outliers).reset_index(drop=True)
summary = (
    grades.groupby("type")["pct"]
    .agg(mean="mean", median="median", std="std", q1=lambda s: s.quantile(0.25), q3=lambda s: s.quantile(0.75))
    .reset_index()
)
summary["iqr"] = summary["q3"] - summary["q1"]
volatile_type = summary.sort_values("std", ascending=False).iloc[0]

fig = px.box(
    grades,
    x="type",
    y="pct",
    color="type",
    points="outliers",
    title="Score Distribution by Assessment Type",
    labels={"type": "Assessment Type", "pct": "Score (%)"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Insight")
st.write(
    f"**{volatile_type['type'].title()}** is the most volatile assessment type "
    f"(std dev {volatile_type['std']:.1f}, IQR {volatile_type['iqr']:.1f}). "
    f"Assignments are the weakest on average at **{summary.sort_values('mean').iloc[0]['mean']:.1f}%**, "
    f"while quizzes show the widest spread in student outcomes."
)

# st.dataframe(
#     summary[["type", "mean", "median", "std", "iqr"]].rename(
#         columns={"type": "Assessment Type", "mean": "Mean", "median": "Median", "std": "Std Dev", "iqr": "IQR"}
#     )
# )
