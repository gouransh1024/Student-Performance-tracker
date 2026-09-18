"""
Class Analytics Page - In-Depth Cohort Intelligence & Diagnostics
Features Performance Heatmap, Attendance Correlation, Grade Donut, and Leaderboard
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.marks import Marks
from models.attendance import Attendance
from utils.ui_theme import inject_custom_theme, render_kpi_card, render_grade_pill, render_sidebar_header
from utils.chart_theme import (
    create_class_heatmap, create_attendance_scatter, 
    create_grade_donut_chart, create_podium_bar_chart
)

st.set_page_config(
    page_title="Class Analytics & Heatmap | ApexTracker",
    page_icon="📊",
    layout="wide"
)

inject_custom_theme()
render_sidebar_header()

st.markdown("""
<div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%); 
            padding: 1.8rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.8rem;
            box-shadow: 0 10px 20px -5px rgba(67, 56, 202, 0.3);">
    <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">
        📊 Class Analytics & Cohort Heatmap
    </h1>
    <p style="color: #E0E7FF; font-size: 0.98rem; margin: 0;">
        Multi-dimensional cohort analysis, Student vs. Subject mastery heatmaps, and attendance regression models.
    </p>
</div>
""", unsafe_allow_html=True)

# Class & Section Filters
unique_classes = Student.get_unique_classes()
if not unique_classes:
    st.warning("⚠️ No student records or classes found. Please enroll students first.")
    st.stop()

col_f1, col_f2 = st.columns([1, 1])
with col_f1:
    selected_class = st.selectbox("Select Target Class:", ["All"] + unique_classes)
with col_f2:
    if selected_class != "All":
        avail_sections = ["All"] + list(set(s[3] for s in Student.get_students_by_class(selected_class)))
        selected_section = st.selectbox("Select Section:", avail_sections)
    else:
        selected_section = "All"

# Fetch cohort data
class_param = None if selected_class == "All" else selected_class
section_param = None if selected_section == "All" else selected_section

class_analytics = Marks.get_class_analytics(class_param, section_param)
students_in_class = Student.get_students_by_class(class_param, section_param) if class_param else Student.get_all_students()

# Cohort Attendance stats
att_summary = Attendance.get_class_attendance_summary(class_param, section_param)
att_rate = att_summary.get('overall_attendance_rate', 0.0)

# Cohort KPIs
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    render_kpi_card("Cohort Size", f"{len(students_in_class)}", "Enrolled Students", "👥", None)
with k2:
    avg_score = class_analytics.get('class_average', 0.0)
    render_kpi_card("Class Average", f"{avg_score:.1f}%", "Overall Score", "📈", "+2.4%", "positive" if avg_score >= 60 else "negative")
with k3:
    pass_pct = class_analytics.get('pass_percentage', 0.0)
    render_kpi_card("Pass Rate", f"{pass_pct:.1f}%", f"{class_analytics.get('pass_count', 0)} Passed", "🏆", None)
with k4:
    att_delta = "positive" if att_rate >= 75 else "negative"
    render_kpi_card("Attendance Rate", f"{att_rate:.1f}%", "Presence Index", "📅", "Target &ge; 75%", att_delta)
with k5:
    fail_cnt = class_analytics.get('fail_count', 0)
    risk_delta = "negative" if fail_cnt > 0 else "positive"
    render_kpi_card("At-Risk Count", f"{fail_cnt}", "Below Passing Threshold", "⚠️", f"{fail_cnt} students", risk_delta)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 1. Performance Heatmap (Students vs Subjects)
st.markdown("### 🔥 Student-Subject Mastery Heatmap")
st.caption("Interactive matrix displaying individual student percentages across subjects to identify learning gaps.")

# Build matrix dataframe
all_marks = Marks.get_all_marks()
cohort_student_ids = set(s[0] for s in students_in_class)

matrix_records = []
for m in all_marks:
    # m is (mark_id, student_name, subject_name, marks_obtained, max_marks, date, type, created, term, student_id, subject_id)
    sid = m[9] if len(m) > 9 else None
    if sid in cohort_student_ids or selected_class == "All":
        pct = Marks.calculate_percentage(m[3], m[4])
        matrix_records.append({
            'Student': m[1],
            'Subject': m[2],
            'Percentage': pct
        })

if matrix_records:
    df_m = pd.DataFrame(matrix_records)
    pivot_df = df_m.pivot_table(index='Student', columns='Subject', values='Percentage', aggfunc='mean')
    st.plotly_chart(create_class_heatmap(pivot_df), use_container_width=True)
else:
    st.info("No marks data logged to construct the mastery heatmap.")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 2. Attendance vs. Performance Correlation Scatter
col_corr1, col_corr2 = st.columns([1, 1])

with col_corr1:
    st.markdown("### 📈 Attendance vs. Academic Score Correlation")
    st.caption("Linear regression showing the empirical relationship between attendance rates and overall grades.")
    corr_data = Attendance.get_all_students_attendance_correlation(class_param, section_param)
    st.plotly_chart(create_attendance_scatter(corr_data), use_container_width=True)

with col_corr2:
    st.markdown("### 🥧 Cohort Grade Distribution")
    st.caption("Proportional breakdown of final letter grades across the class.")
    student_summaries = class_analytics.get('student_summaries', [])
    if student_summaries:
        grade_dist = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'F': 0}
        for s in student_summaries:
            g = s.get('grade', 'N/A')
            grade_dist[g] = grade_dist.get(g, 0) + 1
        st.plotly_chart(create_grade_donut_chart(grade_dist), use_container_width=True)
    else:
        st.info("No summary data available.")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 3. Top Performers Podium & Cohort Ledger
col_pod1, col_pod2 = st.columns([1, 1])

with col_pod1:
    st.markdown("### 🏆 Class Academic Leaderboard")
    top_performers = class_analytics.get('top_performers', [])
    if top_performers:
        df_top = pd.DataFrame(top_performers).rename(columns={'name': 'student_name', 'percentage': 'overall_percentage', 'grade': 'overall_grade'})
        st.plotly_chart(create_podium_bar_chart(df_top), use_container_width=True)
    else:
        st.info("Leaderboard will populate as student assessments are logged.")

with col_pod2:
    st.markdown("### 📋 Student Cohort Summary")
    if student_summaries:
        cohort_table = []
        for s in student_summaries:
            cohort_table.append({
                "Student Name": s.get('name'),
                "Total Marks": f"{s.get('total_obtained')} / {s.get('total_max')}",
                "Percentage": f"{s.get('percentage', 0):.1f}%",
                "Grade": s.get('grade', 'N/A'),
                "Status": "Pass" if s.get('percentage', 0) >= 40 else "Fail",
                "Subjects": s.get('subjects_count')
            })
        df_cohort = pd.DataFrame(cohort_table)
        st.dataframe(df_cohort, use_container_width=True, hide_index=True)

        # Export CSV
        csv_bytes = df_cohort.to_csv(index=False).encode('utf-8')
        class_label = f"Class_{selected_class}_{selected_section}"
        st.download_button(
            label="📥 Export Cohort Analytics (CSV)",
            data=csv_bytes,
            file_name=f"{class_label}_Analytics_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="secondary",
            use_container_width=True
        )
    else:
        st.info("No student summary records found.")
