import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
import base64

from data_loader import get_master, load_groups

# --------------------------------------------------
# Page Title
# --------------------------------------------------
st.title("1. Attendance Rate per Group")
st.markdown(
    "**Business Question:** What is the attendance rate per group, and which groups sit well below the platform average?"
)

# --------------------------------------------------
# Logo
# --------------------------------------------------
logo_path = Path("./images/logo.png")

if logo_path.exists():
    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .fixed-logo {{
            position: fixed;
            top: 3.8rem;
            right: 1rem;
            z-index: 999;
            background: rgba(255,255,255,0);
            border-radius: 12px;
            padding: 8px 10px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12);
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
            <img src="data:image/png;base64,{logo_base64}" alt="Logo"/>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# Load Data
# --------------------------------------------------
master = get_master().copy()
groups = load_groups()

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
# --------------------------------------------------
# Filters
# --------------------------------------------------

st.markdown("### Filters")

col_filter1, col_filter2 = st.columns(2)

group_options = sorted(
    groups["group_name"].dropna().unique().tolist()
)

with col_filter1:
    selected_groups = st.multiselect(
        "Select Group(s)",
        options=group_options,
        default=group_options
    )

if "course" in master.columns:

    course_options = sorted(
        master["course"].dropna().unique().tolist()
    )

    with col_filter2:
        selected_courses = st.multiselect(
            "Select Course(s)",
            options=course_options,
            default=course_options
        )
else:
    selected_courses = None
# --------------------------------------------------
# Apply Filters
# --------------------------------------------------
selected_group_ids = groups.loc[
    groups["group_name"].isin(selected_groups),
    "group_id"
]

filtered = master[
    master["group_id"].isin(selected_group_ids)
].copy()

if (
    selected_courses is not None
    and "course" in filtered.columns
):
    filtered = filtered[
        filtered["course"].isin(selected_courses)
    ]

# --------------------------------------------------
# Empty State
# --------------------------------------------------
if filtered.empty:
    st.warning(
        "No data available for the selected filters."
    )
    st.stop()

# --------------------------------------------------
# Attendance Calculation
# --------------------------------------------------
group_att = (
    filtered.groupby("group_id", as_index=False)
    ["attendance_rate"]
    .mean()
    .merge(
        groups[["group_id", "group_name"]],
        on="group_id",
        how="left"
    )
    .sort_values(
        "attendance_rate",
        ascending=True
    )
)

platform_avg = filtered["attendance_rate"].mean()

# --------------------------------------------------
# Chart
# --------------------------------------------------
fig = px.bar(
    group_att,
    x="group_name",
    y="attendance_rate",
    color="attendance_rate",
    color_continuous_scale="Blues",
    title="Attendance Rate by Group",
    labels={
        "group_name": "Group",
        "attendance_rate": "Attendance Rate (%)",
    },
)

fig.add_hline(
    y=platform_avg,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Platform Avg: {platform_avg:.1f}%"
)

fig.update_layout(
    xaxis_title="Group",
    yaxis_title="Attendance Rate (%)",
    coloraxis_showscale=False
)

fig.update_xaxes(
    tickangle=45
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Platform Average",
        f"{platform_avg:.1f}%"
    )

with col2:
    st.metric(
        "Groups Selected",
        len(selected_groups)
    )

with col3:
    st.metric(
        "Records",
        len(filtered)
    )

# --------------------------------------------------
# Insight Section
# --------------------------------------------------
below_avg = group_att[
    group_att["attendance_rate"] < platform_avg
]

st.subheader("Insight")

if len(below_avg) > 0:

    weakest_group = group_att.iloc[0]

    weak_groups = ", ".join(
        below_avg["group_name"].astype(str)
    )

    st.write(
        f"""
        The filtered dataset has an average attendance rate of
        **{platform_avg:.1f}%**.

        The lowest-performing group is
        **{weakest_group['group_name']}**
        with an attendance rate of
        **{weakest_group['attendance_rate']:.1f}%**.

        Groups currently below the selected population average:

        **{weak_groups}**
        """
    )

else:
    st.write(
        f"""
        All selected groups are at or above the average attendance rate
        of **{platform_avg:.1f}%**.

        Attendance performance is generally healthy across the filtered
        population.
        """
    )
st.subheader("Recommendation")
st.write(
    "Group G07 (C005) sits 15.8 points below the platform average and should be the immediate priority. "
    "Schedule a direct check-in with the assigned instructor to investigate root causes — scheduling conflicts, "
    "session timing, or content difficulty. Consider switching the session day or time if attendance remains "
    "low after outreach. G10 (C007) should be monitored closely as a secondary concern."
)