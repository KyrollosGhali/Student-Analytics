import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import get_master

st.title("10. Age Bands vs Outcomes")
st.markdown("**Business Question:** Bucket students into age bands and compare average grade, attendance, and engagement across them.")
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
master["age"] = pd.to_numeric(master["age"], errors="coerce")
master = master.dropna(subset=["age"])
master["age_band"] = pd.cut(
    master["age"],
    bins=[17, 22, 27, 32, 37, 100],
    labels=["18-22", "23-27", "28-32", "33-37", "38+"],
)

master["video_hours"] = master["total_video_seconds"] / 3600
agg = (
    master.groupby("age_band", observed=True)
    .agg(avg_grade=("avg_grade", "mean"), attendance_rate=("attendance_rate", "mean"), video_hours=("video_hours", "mean"))
    .reset_index()
)

fig = px.bar(
    agg.melt(id_vars="age_band", var_name="metric", value_name="value"),
    x="age_band",
    y="value",
    color="metric",
    barmode="group",
    title="Average Grade, Attendance, and Engagement by Age Band",
    labels={"age_band": "Age Band", "value": "Value", "metric": "Metric"},
)
st.plotly_chart(fig, use_container_width=True)

best_band = agg.sort_values("avg_grade", ascending=False).iloc[0]
st.subheader("Insight")
st.write(
    f"Age effects are small. The strongest band is **{best_band['age_band']}** with an average grade of "
    f"**{best_band['avg_grade']:.1f}%** and attendance near **{best_band['attendance_rate']:.1f}%**. "
    "The populated age bands behave similarly, so age is not a primary driver of outcomes on this platform."
)

st.caption("Method: bucket ages into fixed bands and compare mean grade, attendance, and video-watch time.")
