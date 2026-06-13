import plotly.express as px
import streamlit as st

from data_loader import load_concepts

st.title("6. Concept Failure Rates")
st.markdown("**Business Question:** Across the platform, which concepts have the highest failure rate, and which course do they belong to?")
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
if concepts.empty:
    st.info("No concept performance data available yet.")
    st.stop()

concept_summary = (
    concepts.groupby(["concept_id", "concept_name", "course_id"])
    .agg(total=("mastery_status", "count"), failed=("mastery_status", lambda s: (s == "failed").sum()))
    .reset_index()
)
concept_summary["failure_rate"] = concept_summary["failed"] / concept_summary["total"] * 100
top15 = concept_summary.sort_values("failure_rate", ascending=False).head(15)
weakest = top15.iloc[0]

fig = px.bar(
    top15,
    x="failure_rate",
    y="concept_name",
    color="course_id",
    orientation="h",
    title="Top Concepts by Failure Rate",
    labels={"failure_rate": "Failure Rate (%)", "concept_name": "Concept"},
)
fig.update_yaxes(categoryorder="total ascending")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Insight")
st.write(
    f"**{weakest['concept_name']}** in **{weakest['course_id']}** is the biggest curriculum weak spot, "
    f"with a failure rate of **{weakest['failure_rate']:.1f}%** across {int(weakest['total'])} graded instances."
)

st.session_state["weakest_concept_id"] = weakest["concept_id"]
st.session_state["weakest_concept_name"] = weakest["concept_name"]
st.session_state["weakest_concept_course"] = weakest["course_id"]

st.caption("Method: failure rate = failed outcomes divided by all graded attempts for each concept.")
