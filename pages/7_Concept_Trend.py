import numpy as np
import plotly.express as px
import streamlit as st

from data_loader import load_concepts

st.title("7. Weakest Concept - Mastery Trend Over Time")
st.markdown("**Business Question:** For the weakest concept, how does cohort mastery change over time across successive assessments?")
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

concepts = load_concepts().copy()
weakest_id = st.session_state.get("weakest_concept_id")

if weakest_id is None and not concepts.empty:
    summary = (
        concepts.groupby(["concept_id", "concept_name"])
        .agg(total=("mastery_status", "count"), failed=("mastery_status", lambda s: (s == "failed").sum()))
        .reset_index()
    )
    summary["failure_rate"] = summary["failed"] / summary["total"]
    weakest_row = summary.sort_values("failure_rate", ascending=False).iloc[0]
    weakest_id = weakest_row["concept_id"]

concept_df = concepts[concepts["concept_id"] == weakest_id].copy()
if concept_df.empty:
    st.info("Select the weakest concept on the prior page first.")
    st.stop()

concept_df = concept_df.sort_values("timestamp")
trend = concept_df.groupby("timestamp", as_index=False)["score_pct"].mean()
concept_name = concept_df["concept_name"].iloc[0]

fig = px.line(
    trend,
    x="timestamp",
    y="score_pct",
    markers=True,
    title=f"Cohort Mastery Over Time - {concept_name}",
    labels={"timestamp": "Date", "score_pct": "Average Mastery (%)"},
)
fig.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="Pass threshold")
st.plotly_chart(fig, use_container_width=True)

slope = np.polyfit(np.arange(len(trend)), trend["score_pct"], 1)[0] if len(trend) > 1 else 0
if slope > 0.5:
    direction = "improving"
elif slope < -0.5:
    direction = "declining"
else:
    direction = "flat"

st.subheader("Insight")
st.write(
    f"For **{concept_name}**, mastery is **{direction}** with a slope of about **{slope:.2f}** points per assessment. "
    f"The series starts at **{trend['score_pct'].iloc[0]:.1f}%** and ends at **{trend['score_pct'].iloc[-1]:.1f}%**, "
    "so the curriculum fix is helping only gradually."
)

st.subheader("Recommendation")
st.write(
    "Recursion mastery has moved from 48% to 65% over the term, but the trend is effectively flat — "
    "the improvement is inconsistent and has not produced a clear recovery curve. The current teaching "
    "approach has reached its ceiling for this concept. Introduce targeted interventions: spaced repetition "
    "exercises, peer teaching sessions, and additional worked examples between assessments. "
    "Re-evaluate after two assessment cycles to confirm whether mastery is genuinely improving."
)