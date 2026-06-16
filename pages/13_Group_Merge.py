import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

from data_loader import load_concepts, load_groups, load_students

st.title("13. Group Merge Recommendation")
st.markdown("**Business Question:** Identify any group that is too small to be viable.")
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

students = load_students().copy()
groups = load_groups().copy()
concepts = load_concepts().copy()

true_counts = students.groupby("group_id").size().reset_index(name="true_count")
audit = groups.merge(true_counts, on="group_id", how="left").fillna(0)
smallest = audit.sort_values("true_count").iloc[0]

st.write(
    f"**Smallest group:** {smallest['group_name']} ({smallest['group_id']}) with "
    f"**{int(smallest['true_count'])} student(s)**."
)

profile = concepts.pivot_table(index="student_id", columns="concept_id", values="score_pct", aggfunc="mean").fillna(0)
student_groups = students[["student_id", "group_id"]]
group_profiles = (
    profile.reset_index()
    .merge(student_groups, on="student_id", how="left")
    .groupby("group_id")
    .mean(numeric_only=True)
)

similarity = pd.DataFrame(
    cosine_similarity(group_profiles),
    index=group_profiles.index,
    columns=group_profiles.index,
)

fig = px.imshow(
    similarity,
    text_auto=".2f",
    color_continuous_scale="Blues",
    title="Concept-Mastery Similarity Between Groups",
    labels={"x": "Group ID", "y": "Group ID", "color": "Similarity"},
)
st.plotly_chart(fig, use_container_width=True)

closest_group = similarity.loc[smallest["group_id"]].drop(smallest["group_id"]).idxmax()
closest_score = similarity.loc[smallest["group_id"], closest_group]
closest_name = groups.loc[groups["group_id"] == closest_group, "group_name"].iloc[0]

st.subheader("Insight")
st.write(
    f"{smallest['group_name']} is too small to be a viable standalone cohort. "
    f"Its closest concept-mastery match is **{closest_name}** ({closest_group}) with similarity **{closest_score:.2f}**. "
    "If scheduling and course alignment allow, that is the best merge candidate."
)

st.subheader("Recommendation")
st.write(
    "G10 with one enrolled student is not a viable standalone teaching group and should not continue "
    "as an independent cohort. Since no other group currently studies C007, the most practical options are: "
    "(1) reassign the student to the closest concept-profile match in another group after confirming "
    "course equivalence, or (2) hold C007 as a pilot cohort intentionally and document it as such "
    "so it is excluded from group-level performance comparisons. Either way, a decision should be made "
    "immediately to avoid wasting instructor time and platform resources on a single-student cohort."
)