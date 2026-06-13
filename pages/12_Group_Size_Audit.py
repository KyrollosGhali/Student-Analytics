import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_groups, load_students

st.title("12. Group Size Audit")
st.markdown("**Business Question:** Compute the true group sizes from students and compare them to the self-reported counts in groups.")
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

true_counts = students.groupby("group_id").size().reset_index(name="true_count")
audit = groups.merge(true_counts, on="group_id", how="left").fillna(0)
audit["true_count"] = pd.to_numeric(audit["true_count"], errors="coerce").fillna(0)
audit["stated_num_students"] = pd.to_numeric(audit["stated_num_students"], errors="coerce").fillna(0)
audit["discrepancy"] = audit["true_count"] - audit["stated_num_students"]
audit["abs_discrepancy"] = audit["discrepancy"].abs()

plot_df = audit.melt(
    id_vars=["group_id", "group_name"],
    value_vars=["stated_num_students", "true_count"],
    var_name="metric",
    value_name="count",
)

fig = px.bar(
    plot_df,
    x="group_name",
    y="count",
    color="metric",
    barmode="group",
    title="True Group Size vs Stated Size",
    labels={"group_name": "Group", "count": "Students", "metric": "Count Type"},
)
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, use_container_width=True)

flagged = audit[audit["abs_discrepancy"] >= 3].sort_values("abs_discrepancy", ascending=False)

st.subheader("Insight")
if flagged.empty:
    st.write("No suspicious discrepancies were found. Stated sizes broadly align with the live roster.")
else:
    st.write(
        f"**{len(flagged)} groups** differ from the live roster by 3 or more students. "
        f"The largest gaps are **{', '.join(flagged['group_name'].astype(str).head(3))}**. "
        "These inconsistencies are large enough to affect staffing and capacity decisions."
    )

# st.dataframe(
#     audit[["group_id", "group_name", "stated_num_students", "true_count", "discrepancy"]].rename(
#         columns={
#             "group_id": "Group ID",
#             "group_name": "Group",
#             "stated_num_students": "Stated Count",
#             "true_count": "True Count",
#             "discrepancy": "Difference",
#         }
#     )
# )

st.caption("Method: count students per group from the roster and compare that count with the stated group size.")
