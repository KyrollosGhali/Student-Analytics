import json

import numpy as np
import pandas as pd
import streamlit as st

from db import load_collection


def _empty_df(columns):
    return pd.DataFrame(columns=columns)


@st.cache_data(ttl=600)
def load_courses():
    df = load_collection("courses")
    if df.empty:
        return _empty_df(["course_id", "course_name", "category", "difficulty_level", "duration_weeks", "short_description", "modules", "is_active"])

    if "modules" in df.columns:
        def parse_modules(value):
            if isinstance(value, list):
                return value
            try:
                return json.loads(value)
            except Exception:
                return []

        df["modules_list"] = df["modules"].apply(parse_modules)
    return df


@st.cache_data(ttl=600)
def load_groups():
    df = load_collection("groups")
    if df.empty:
        return _empty_df(["group_id", "group_name", "course_id", "stated_num_students", "session_day", "session_time", "instructor"])

    if "group_name" in df.columns:
        df["group_name"] = (
            df["group_name"]
            .astype(str)
            .str.replace("Ã¢â‚¬â€", "-", regex=False)
            .str.replace("â€”", "-", regex=False)
            .str.replace("—", "-", regex=False)
            .str.strip()
        )
    if "stated_num_students" in df.columns:
        df["stated_num_students"] = pd.to_numeric(df["stated_num_students"], errors="coerce")
    return df


@st.cache_data(ttl=600)
def load_students():
    df = load_collection("students")
    if df.empty:
        return _empty_df(["student_id", "full_name", "age", "gender", "city", "email", "group_id", "enrollment_date"])

    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
    if "enrollment_date" in df.columns:
        df["enrollment_date"] = pd.to_datetime(df["enrollment_date"], errors="coerce")
    return df


@st.cache_data(ttl=600)
def load_grades():
    df = load_collection("grades")
    if df.empty:
        return _empty_df(["grade_id", "assessment_id", "assessment_title", "type", "score", "max_score", "date", "student_id", "group_id", "pct"])

    if "assessment_id" not in df.columns:
        rows = []
        list_cols = [c for c in df.columns if len(df) and isinstance(df[c].iloc[0], list)]
        list_col = list_cols[0] if list_cols else None
        for _, row in df.iterrows():
            base = row.drop(labels=[list_col]) if list_col else row
            items = row[list_col] if list_col else [row]
            for item in items:
                rows.append({**base.to_dict(), **item})
        df = pd.DataFrame(rows)

    if "group_id" not in df.columns and "student_id" in df.columns:
        students = load_students()
        if not students.empty and "group_id" in students.columns:
            df = df.merge(students[["student_id", "group_id"]], on="student_id", how="left")

    for col in ["date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["score", "max_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "score" in df.columns and "max_score" in df.columns:
        df["pct"] = df["score"] / df["max_score"] * 100
    else:
        df["pct"] = np.nan

    return df


@st.cache_data(ttl=600)
def load_concepts():
    df = load_collection("concept_performance")
    if df.empty:
        return _empty_df(["record_id", "student_id", "course_id", "assessment_id", "question_no", "concept_id", "concept_name", "score_pct", "mastery_status", "timestamp"])

    if "score_pct" in df.columns:
        df["score_pct"] = pd.to_numeric(df["score_pct"], errors="coerce")
    else:
        df["score_pct"] = np.nan

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        df["timestamp"] = pd.NaT

    return df


@st.cache_data(ttl=600)
def load_engagement():
    df = load_collection("engagement_events")
    if df.empty:
        return _empty_df(["event_id", "student_id", "event_type", "event_datetime", "duration_seconds", "device", "hour", "day"])

    if "event_datetime" in df.columns:
        df["event_datetime"] = pd.to_datetime(df["event_datetime"], errors="coerce")
    if "duration_seconds" in df.columns:
        df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce")
    else:
        df["duration_seconds"] = np.nan
    return df


@st.cache_data(ttl=600)
def load_submissions():
    df = load_collection("assignment_submission")
    if df.empty:
        return _empty_df(["submission_id", "student_id", "course_id", "assessment_id", "deadline", "submitted_at", "is_late", "time_spent_minutes", "attempts", "is_late_computed", "buffer_hours"])

    for col in ["deadline", "submitted_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.NaT

    for col in ["time_spent_minutes", "attempts"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    df["is_late_computed"] = df["submitted_at"] > df["deadline"]
    df["buffer_hours"] = (df["deadline"] - df["submitted_at"]).dt.total_seconds() / 3600
    return df


@st.cache_data(ttl=600)
def load_attendance():
    df = load_collection("attendance")
    if df.empty:
        return _empty_df(["record_id", "student_id", "group_id", "session_type", "session_datetime", "status", "day_name"])

    rename_map = {
        "Record ID": "record_id",
        "RecordID": "record_id",
        "Student ID": "student_id",
        "StudentID": "student_id",
        "Group ID": "group_id",
        "GroupID": "group_id",
        "Session Type": "session_type",
        "SessionType": "session_type",
        "Date": "session_datetime",
        "Session Date": "session_datetime",
        "DateTime": "session_datetime",
        "Datetime": "session_datetime",
        "Status": "status",
        "Attendance": "status",
        "Attendance Status": "status",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    if "session_datetime" in df.columns:
        df["session_datetime"] = pd.to_datetime(df["session_datetime"], errors="coerce")

    if "status" in df.columns:
        status_map = {
            "attended": "attended",
            "present": "attended",
            "yes": "attended",
            "1": "attended",
            "p": "attended",
            "absent": "absent",
            "no": "absent",
            "0": "absent",
            "a": "absent",
        }
        df["status"] = df["status"].astype(str).str.strip().str.lower().map(status_map)
        df = df[df["status"].isin(["attended", "absent"])]

    return df


@st.cache_data(ttl=600)
def get_master():
    students = load_students()
    groups = load_groups()
    grades = load_grades()
    attendance = load_attendance()
    engagement = load_engagement()
    concepts = load_concepts()

    if not students.empty and not groups.empty:
        students = students.merge(groups[["group_id", "course_id", "group_name"]], on="group_id", how="left")
    elif "group_name" not in students.columns:
        students["group_name"] = np.nan
        students["course_id"] = np.nan

    att_summary = (
        attendance.groupby("student_id")["status"]
        .apply(lambda s: (s == "attended").mean() * 100)
        .reset_index(name="attendance_rate")
        if not attendance.empty else _empty_df(["student_id", "attendance_rate"])
    )

    grade_summary = (
        grades.groupby("student_id")["pct"].mean().reset_index(name="avg_grade")
        if not grades.empty else _empty_df(["student_id", "avg_grade"])
    )

    engagement_count = (
        engagement.groupby("student_id").size().reset_index(name="engagement_count")
        if not engagement.empty else _empty_df(["student_id", "engagement_count"])
    )

    login_count = (
        engagement[engagement["event_type"].astype(str).str.lower() == "login"]
        .groupby("student_id").size().reset_index(name="login_count")
        if (not engagement.empty and "event_type" in engagement.columns) else _empty_df(["student_id", "login_count"])
    )

    video_time = (
        engagement[engagement["event_type"].astype(str).str.lower().str.contains("video")]
        .groupby("student_id")["duration_seconds"].sum().reset_index(name="total_video_seconds")
        if (not engagement.empty and "event_type" in engagement.columns) else _empty_df(["student_id", "total_video_seconds"])
    )

    failed = (
        concepts[concepts["mastery_status"] == "failed"]
        .groupby("student_id").size().reset_index(name="failed_concepts_count")
        if not concepts.empty else _empty_df(["student_id", "failed_concepts_count"])
    )

    master = students.copy()
    for summary in [att_summary, grade_summary, engagement_count, login_count, video_time, failed]:
        master = master.merge(summary, on="student_id", how="left")

    for c in ["attendance_rate", "avg_grade", "engagement_count", "login_count", "total_video_seconds", "failed_concepts_count"]:
        if c not in master.columns:
            master[c] = 0
        master[c] = master[c].fillna(0)

    master["video_hours"] = master["total_video_seconds"] / 3600
    return master
