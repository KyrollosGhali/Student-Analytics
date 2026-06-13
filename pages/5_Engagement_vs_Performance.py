import plotly.express as px
import streamlit as st
from scipy.stats import pearsonr

from data_loader import get_master

st.title("5. Engagement vs Academic Performance")
st.markdown("**Business Question:** Does engagement relate to academic performance?")
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
clean = master[master["avg_grade"] > 0].copy()
clean["video_hours"] = clean["total_video_seconds"] / 3600

if len(clean) < 2:
    st.info("Not enough performance data to calculate engagement relationships.")
    st.stop()

r_events, p_events = pearsonr(clean["engagement_count"], clean["avg_grade"])
r_video, p_video = pearsonr(clean["video_hours"], clean["avg_grade"])

left, right = st.columns(2)
with left:
    fig1 = px.scatter(
        clean,
        x="engagement_count",
        y="avg_grade",
        trendline="ols",
        opacity=0.65,
        title=f"Engagement Count vs Average Grade (r = {r_events:.2f})",
        labels={"engagement_count": "Engagement Events", "avg_grade": "Average Grade (%)"},
    )
    st.plotly_chart(fig1, use_container_width=True)

with right:
    fig2 = px.scatter(
        clean,
        x="video_hours",
        y="avg_grade",
        trendline="ols",
        opacity=0.65,
        title=f"Video-Watch Time vs Average Grade (r = {r_video:.2f})",
        labels={"video_hours": "Video Watch Time (hours)", "avg_grade": "Average Grade (%)"},
    )
    st.plotly_chart(fig2, use_container_width=True)

corr = clean[["engagement_count", "video_hours", "avg_grade"]].corr()
corr.index = ["Engagement Events", "Video Watch Hours", "Average Grade"]
corr.columns = ["Engagement Events", "Video Watch Hours", "Average Grade"]
fig3 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="Blues",
    title="Engagement and Performance Correlation Heatmap",
)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Insight")
st.write(
    f"Engagement has a positive relationship with performance, with event count at r = {r_events:.2f} "
    f"and video-watch time at r = {r_video:.2f}. "
    "The dataset does not contain true login events, so video activity is the most reliable engagement proxy available."
)

st.caption("Method: Pearson correlations between performance and engagement proxies, plus a correlation heatmap.")
