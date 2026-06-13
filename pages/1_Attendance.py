import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import get_master, load_groups

st.title("1. Attendance Rate per Group")
st.markdown("**Business Question:** What is the attendance rate per group, and which groups sit well below the platform average?")
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
groups = load_groups()

group_att = (
    master.groupby("group_id", as_index=False)["attendance_rate"]
    .mean()
    .merge(groups[["group_id", "group_name"]], on="group_id", how="left")
    .sort_values("attendance_rate")
)
platform_avg = master["attendance_rate"].mean()

fig = px.bar(
    group_att,
    x="group_name",
    y="attendance_rate",
    color="attendance_rate",
    color_continuous_scale="Blues",
    title="Attendance Rate by Group",
    labels={"group_name": "Group", "attendance_rate": "Attendance Rate (%)"},
)
fig.add_hline(
    y=platform_avg,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Platform Avg: {platform_avg:.1f}%",
)
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, use_container_width=True)

below_avg = group_att[group_att["attendance_rate"] < platform_avg]

st.subheader("Insight")
if len(below_avg):
    weak_groups = ", ".join(below_avg["group_name"].astype(str))
    st.write(
        f"The platform average attendance rate is **{platform_avg:.1f}%**. "
        f"Two groups sit below the mean, led by **{group_att.iloc[0]['group_name']}** at "
        f"**{group_att.iloc[0]['attendance_rate']:.1f}%**. "
        f"These groups need the fastest intervention: {weak_groups}."
    )
else:
    st.write(
        f"All groups are at or above the platform average attendance rate of **{platform_avg:.1f}%**. "
        "Attendance is broadly healthy, so the main opportunity is to keep the lower-performing groups from slipping."
    )

st.caption("Method: mean student attendance rate aggregated by group, compared against the platform-wide mean.")
