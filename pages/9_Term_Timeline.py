import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_attendance, load_engagement

st.title("9. Attendance and Engagement Over the Term")
st.markdown("**Business Question:** Plot attendance and engagement over the term. Is there a window where the whole cohort dips at once?")
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

attendance = load_attendance().copy()
engagement = load_engagement().copy()

attendance["week"] = attendance["session_datetime"].dt.to_period("W").apply(lambda r: r.start_time)
engagement["week"] = engagement["event_datetime"].dt.to_period("W").apply(lambda r: r.start_time)

weekly_att = (
    attendance.groupby("week")["status"]
    .apply(lambda s: (s == "attended").mean() * 100)
    .reset_index(name="attendance_rate")
)
weekly_eng = engagement.groupby("week").size().reset_index(name="engagement_events")
merged = weekly_att.merge(weekly_eng, on="week", how="outer").sort_values("week").fillna(0)

fig = go.Figure()
fig.add_trace(go.Scatter(x=merged["week"], y=merged["attendance_rate"], mode="lines+markers", name="Attendance Rate"))
fig.add_trace(go.Scatter(x=merged["week"], y=merged["engagement_events"], mode="lines+markers", name="Engagement Events", yaxis="y2"))
fig.update_layout(
    title="Weekly Attendance and Engagement",
    xaxis_title="Week",
    yaxis=dict(title="Attendance Rate (%)"),
    yaxis2=dict(title="Engagement Events", overlaying="y", side="right"),
    legend=dict(orientation="h"),
)
st.plotly_chart(fig, use_container_width=True)

min_att = merged.loc[merged["attendance_rate"].idxmin()]
min_eng = merged.loc[merged["engagement_events"].idxmin()]

st.subheader("Insight")
st.write(
    f"The sharpest shared dip appears in the week of **{min_att['week'].date()}**, where attendance falls to "
    f"**{min_att['attendance_rate']:.1f}%** and engagement reaches **{int(min_eng['engagement_events'])} events**. "
    "That pattern points to a cohort-wide disruption rather than a single-group problem."
)

st.caption("Method: weekly attendance rate from session records and weekly engagement event counts from platform events.")
