# 🎓 Kayfa Platform Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-black)
![License](https://img.shields.io/badge/License-Educational-orange)

A comprehensive **Streamlit analytics dashboard** built to answer **15 key business questions** about student attendance, engagement, academic performance, cohort quality, and risk prediction on the **Kayfa Learning Platform**.

The project combines data from multiple sources, stores it in **MongoDB Atlas**, performs analytical processing using **Pandas and Scikit-Learn**, and delivers actionable insights through interactive visualizations.

---

## 🚀 Business Objectives

This dashboard helps stakeholders:

* Identify low-performing groups
* Detect at-risk students early
* Understand attendance-performance relationships
* Evaluate course effectiveness
* Analyze engagement patterns
* Improve curriculum quality
* Support operational planning
* Optimize student grouping strategies

---

## 📊 Dashboard Coverage

The dashboard answers 15 analytics questions across five major domains:

| Domain               | Questions               |
| -------------------- | ----------------------- |
| Attendance Analytics | Q1, Q4, Q9              |
| Academic Performance | Q2, Q3, Q10             |
| Engagement Analysis  | Q5, Q8                  |
| Learning Outcomes    | Q6, Q7                  |
| Risk & Operations    | Q11, Q12, Q13, Q14, Q15 |

---

## 🗄️ Data Sources

| Collection               | Description                             |
| ------------------------ | --------------------------------------- |
| `courses`                | Course catalogue and module information |
| `students`               | Student roster and enrollment data      |
| `groups`                 | Cohort information                      |
| `grades`                 | Assessment results                      |
| `attendance`             | Monthly attendance records              |
| `concepts_performance`   | Concept mastery measurements            |
| `engagement_events`      | Student activity logs                   |
| `assignment_submissions` | Assignment submission records           |

---

## ⚠️ Data Quality Notes

### Engagement Data

Only `video_watch` events are available.

Unavailable metrics include:

* Login frequency
* Discussion activity
* Platform navigation behavior
* Assignment viewing history

Therefore engagement metrics rely on:

* Total watch time
* Number of watch events

### Group Size Reliability

The field:

```text
groups.stated_num_students
```

is self-reported and differs from actual enrollment counts.

The dashboard uses:

```text
students collection
```

as the source of truth for roster calculations.

### Outlier Cohort

Course **C007** contains only **one enrolled student** and is treated as a non-comparable outlier in course-level analyses.

---

## 📈 Key Findings

| Question | Main Insight                                                   |
| -------- | -------------------------------------------------------------- |
| Q1       | G07-C005 attendance is 15.8 percentage points below average    |
| Q2       | Quiz scores show the highest variability                       |
| Q3       | C001 is the strongest course, C005 the weakest                 |
| Q4       | Attendance moderately correlates with grades (r=0.42)          |
| Q5       | Engagement positively correlates with performance              |
| Q6       | Recursion exhibits the highest failure rate                    |
| Q7       | Weak concept mastery remains largely unchanged over time       |
| Q8       | Late submissions reduce average score by 4.6 points            |
| Q9       | Platform-wide engagement dip observed during March             |
| Q10      | Age has minimal effect on outcomes                             |
| Q11      | Four student segments identified via clustering                |
| Q12      | 86-student discrepancy between reported and actual group sizes |
| Q13      | G10 is operationally non-viable                                |
| Q14      | Risk rankings are dominated by G07 students                    |
| Q15      | Most groups show flat or declining grade trends                |

---

## 🏗️ System Architecture

```text
Excel Files
JSON Records
MongoDB Collections
        │
        ▼
 Data Cleaning & Transformation
        │
        ▼
      MongoDB Atlas
        │
        ▼
     Streamlit App
        │
        ▼
 Interactive Analytics Dashboard
```

---

## 📂 Project Structure

```text
kayfa_dashboard/
├── app.py
├── db.py
├── data_loader.py
├── requirements.txt
└── pages/
    ├── 1_Attendance.py
    ├── 2_Scores_Distribution.py
    ├── 3_Course_Performance.py
    ├── 4_Attendance_vs_Grade.py
    ├── 5_Engagement_vs_Performance.py
    ├── 6_Concept_Failure_Rates.py
    ├── 7_Concept_Trend.py
    ├── 8_Late_Submissions.py
    ├── 9_Term_Timeline.py
    ├── 10_Age_Bands.py
    ├── 11_Segmentation.py
    ├── 12_Group_Size_Audit.py
    ├── 13_Group_Merge.py
    ├── 14_At_Risk_Ranking.py
    └── 15_Group_Trends.py
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone <repository-url>
cd kayfa_dashboard
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Secrets

Create:

```text
.streamlit/secrets.toml
```

```toml
MONGO_URI = "mongodb+srv://<user>:<password>@cluster.mongodb.net/"
MONGO_DB = "kayfa"
```

### Run Dashboard

```bash
streamlit run app.py
```

---

## ☁️ Deployment

The dashboard can be deployed on:

* Streamlit Community Cloud
* Render
* Railway
* Azure App Service
* AWS EC2
* Docker Containers

MongoDB Atlas is used as the production database backend.

---

## 🎯 Final Recommendations

### High Priority

* Investigate Group 07 attendance issues
* Provide intervention for high-risk students
* Review Course C005 content quality

### Curriculum Improvements

* Redesign Recursion teaching strategy in C002
* Reevaluate assessments with unusually high failure rates

### Operational Improvements

* Reconcile reported group sizes with actual rosters
* Review viability of Group G10

### Data Improvements

* Capture login activity
* Track forum participation
* Store assignment view events
* Expand engagement metrics beyond video consumption

---

## 👨‍💻 Tech Stack

* Python
* Pandas
* NumPy
* SciPy
* Scikit-Learn
* MongoDB Atlas
* Streamlit
* Plotly Express
* Plotly Graph Objects

---

Built as part of the **Kayfa Learning Platform Analytics Project** to support data-driven educational decision making.
## 🎥 Live Demo

### Dashboard Walkthrough

Watch the dashboard in action:

🔗 **Demo Video:** 
![Demo](Student Analysis demp1.mp4)
### Key Features Demonstrated

* Interactive attendance analytics
* Student performance exploration
* Engagement vs performance analysis
* Concept mastery tracking
* Student segmentation using K-Means clustering
* At-risk student identification
* Group size auditing and optimization insights

