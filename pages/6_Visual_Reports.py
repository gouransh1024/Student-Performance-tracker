"""
Visual Reports Page - Executive Academic Visualizations & Trends
Enhanced with Unified Design System and Interactive Plotly Engine
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.subject import Subject
from models.marks import Marks
from utils.analytics import PerformanceAnalytics
from utils.ui_theme import inject_custom_theme, render_kpi_card, render_sidebar_header
from utils.chart_theme import apply_chart_style

st.set_page_config(
    page_title="Visual Reports & Analytics | ApexTracker",
    page_icon="📈",
    layout="wide"
)

inject_custom_theme()

st.markdown("""
<div style="background: linear-gradient(135deg, #0F172A 0%, #312E81 100%); 
            padding: 1.8rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.8rem;
            box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.3);">
    <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">
        📈 Executive Visual Reports & Longitudinal Trends
    </h1>
    <p style="color: #C7D2FE; font-size: 0.98rem; margin: 0;">
        Interactive multidimensional charts, subject variance distributions, and longitudinal cohort tracking.
    </p>
</div>
""", unsafe_allow_html=True)

# Data verification
students = Student.get_all_students()
marks = Marks.get_all_marks()

if not students or not marks:
    st.warning("⚠️ Insufficient data for visual reports. Please ensure students and marks are registered.")
    st.stop()

# Sidebar Navigation
with st.sidebar:
    render_sidebar_header()
    st.subheader("📊 Visualization Module")
    chart_category = st.radio(
        "Select Visual Dimension:",
        [
            "Grade Distribution",
            "Class-Wise Performance",
            "Subject Mastery & Variance",
            "Longitudinal Trends",
            "Pass / Fail Diagnostic"
        ]
    )

    st.markdown("---")
    st.subheader("Cohort Filters")
    unique_classes = Student.get_unique_classes()
    selected_class = st.selectbox("Filter Class:", ["All"] + unique_classes)
    
    if selected_class != "All":
        avail_sections = ["All"] + list(set(s[3] for s in Student.get_students_by_class(selected_class)))
        selected_sec = st.selectbox("Filter Section:", avail_sections)
    else:
        selected_sec = "All"

class_param = None if selected_class == "All" else selected_class
section_param = None if selected_sec == "All" else selected_sec

# 1. Grade Distribution
if chart_category == "Grade Distribution":
    st.subheader("📊 Cohort Grade Distribution Analysis")
    grade_data = PerformanceAnalytics.get_grade_distribution(class_param, section_param)

    if grade_data['total_students'] > 0:
        counts = grade_data['grade_counts']
        df_grades = pd.DataFrame([
            {'Grade': g, 'Count': c, 'Percentage': (c / grade_data['total_students']) * 100}
            for g, c in counts.items() if c > 0
        ])

        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(
                df_grades, values='Count', names='Grade',
                title=f"Letter Grade Breakdown (Total: {grade_data['total_students']} Students)",
                color='Grade',
                color_discrete_map={
                    'A+': '#10B981', 'A': '#06B6D4', 'B+': '#3B82F6', 
                    'B': '#6366F1', 'C+': '#F59E0B', 'C': '#F97316', 'F': '#EF4444'
                },
                hole=0.45
            )
            st.plotly_chart(apply_chart_style(fig_pie, height=400), use_container_width=True)

        with col2:
            fig_bar = px.bar(
                df_grades, x='Grade', y='Count',
                title="Student Frequency per Grade Bracket",
                color='Grade',
                color_discrete_map={
                    'A+': '#10B981', 'A': '#06B6D4', 'B+': '#3B82F6', 
                    'B': '#6366F1', 'C+': '#F59E0B', 'C': '#F97316', 'F': '#EF4444'
                }
            )
            st.plotly_chart(apply_chart_style(fig_bar, height=400), use_container_width=True)

        # Export
        csv_bytes = df_grades.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Grade Distribution (CSV)", csv_bytes, "grade_distribution.csv", "text/csv")
    else:
        st.info("No grade data available for this selection.")

# 2. Class Performance
elif chart_category == "Class-Wise Performance":
    st.subheader("🏫 Cross-Class Comparative Analytics")
    class_perf = PerformanceAnalytics.get_class_wise_performance()

    if class_perf:
        df_cp = pd.DataFrame(class_perf)
        df_cp['Cohort'] = df_cp['class'] + '-' + df_cp['section']

        col1, col2 = st.columns(2)
        with col1:
            fig_cp_avg = px.bar(
                df_cp, x='Cohort', y='avg_percentage',
                title="Mean Academic Percentage by Cohort (%)",
                color='avg_percentage',
                color_continuous_scale='Tealgrn'
            )
            st.plotly_chart(apply_chart_style(fig_cp_avg, height=400), use_container_width=True)

        with col2:
            fig_cp_pass = px.bar(
                df_cp, x='Cohort', y='pass_percentage',
                title="Cohort Pass Rate (%)",
                color='pass_percentage',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(apply_chart_style(fig_cp_pass, height=400), use_container_width=True)

        st.dataframe(df_cp[['Cohort', 'total_students', 'avg_percentage', 'pass_percentage', 'total_assessments']], use_container_width=True, hide_index=True)
        csv_bytes = df_cp.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Cross-Class Data (CSV)", csv_bytes, "class_comparison.csv", "text/csv")
    else:
        st.info("No comparative class data available.")

# 3. Subject Mastery & Variance
elif chart_category == "Subject Mastery & Variance":
    st.subheader("📚 Subject Competency & Range Analysis")
    subj_perf = PerformanceAnalytics.get_subject_performance_comparison()

    if subj_perf:
        df_sp = pd.DataFrame(subj_perf)
        col1, col2 = st.columns(2)
        with col1:
            fig_s_avg = px.bar(
                df_sp, y='subject', x='avg_percentage', orientation='h',
                title="Subject Average Mastery (%)",
                color='avg_percentage',
                color_continuous_scale='Purples'
            )
            st.plotly_chart(apply_chart_style(fig_s_avg, height=450), use_container_width=True)

        with col2:
            fig_s_cnt = px.bar(
                df_sp, y='subject', x='total_assessments', orientation='h',
                title="Total Conducted Assessments",
                color='total_assessments',
                color_continuous_scale='Sunset'
            )
            st.plotly_chart(apply_chart_style(fig_s_cnt, height=450), use_container_width=True)

        # Range chart
        fig_rng = go.Figure()
        for _, row in df_sp.iterrows():
            fig_rng.add_trace(go.Scatter(
                x=[row['lowest_marks'], row['highest_marks']],
                y=[row['subject'], row['subject']],
                mode='lines+markers',
                name=row['subject'],
                line=dict(width=4, color='#4F46E5'),
                marker=dict(size=8, color='#06B6D4')
            ))
        fig_rng.update_layout(title="Min-Max Score Dispersion by Subject", xaxis_title="Score", showlegend=False)
        st.plotly_chart(apply_chart_style(fig_rng, height=420), use_container_width=True)

        csv_bytes = df_sp.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Subject Diagnostics (CSV)", csv_bytes, "subject_diagnostics.csv", "text/csv")
    else:
        st.info("No subject marks found.")

# 4. Longitudinal Trends
elif chart_category == "Longitudinal Trends":
    st.subheader("📈 Longitudinal Assessment Trends")
    trend_rows = []
    for m in marks:
        pct = Marks.calculate_percentage(m[3], m[4])
        term_val = m[8] if len(m) > 8 and m[8] else "Term 1"
        trend_rows.append({
            'Date': m[5],
            'Student': m[1],
            'Subject': m[2],
            'Score %': pct,
            'Assessment Type': m[6],
            'Term': term_val
        })

    df_t = pd.DataFrame(trend_rows)
    df_t['Date'] = pd.to_datetime(df_t['Date'])

    if not df_t.empty:
        col1, col2 = st.columns(2)
        with col1:
            df_day = df_t.groupby('Date')['Score %'].mean().reset_index()
            fig_line = px.line(
                df_day, x='Date', y='Score %',
                title="Average Performance Over Time",
                markers=True
            )
            fig_line.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="Passing Threshold (40%)")
            st.plotly_chart(apply_chart_style(fig_line, height=400), use_container_width=True)

        with col2:
            df_type = df_t.groupby('Assessment Type')['Score %'].mean().reset_index()
            fig_type = px.bar(
                df_type, x='Assessment Type', y='Score %',
                title="Average Score by Assessment Category",
                color='Score %',
                color_continuous_scale='Spectral'
            )
            st.plotly_chart(apply_chart_style(fig_type, height=400), use_container_width=True)

        csv_bytes = df_t.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Trend Records (CSV)", csv_bytes, "assessment_trends.csv", "text/csv")
    else:
        st.info("No timeline data available.")

# 5. Pass / Fail Diagnostic
elif chart_category == "Pass / Fail Diagnostic":
    st.subheader("✅❌ Pass / Fail Diagnostics & Risk Profiling")
    pass_fail_records = []
    for m in marks:
        pct = Marks.calculate_percentage(m[3], m[4])
        pass_fail_records.append({
            'Student': m[1],
            'Subject': m[2],
            'Score %': pct,
            'Status': 'Pass' if pct >= 40 else 'Fail',
            'Type': m[6]
        })

    df_pf = pd.DataFrame(pass_fail_records)
    col1, col2 = st.columns(2)
    with col1:
        status_counts = df_pf['Status'].value_counts()
        fig_pf = px.pie(
            values=status_counts.values, names=status_counts.index,
            title="Cohort Pass vs. Fail Ratio",
            color=status_counts.index,
            color_discrete_map={'Pass': '#10B981', 'Fail': '#EF4444'},
            hole=0.4
        )
        st.plotly_chart(apply_chart_style(fig_pf, height=380), use_container_width=True)

    with col2:
        sub_pf = df_pf.groupby(['Subject', 'Status']).size().unstack(fill_value=0).reset_index()
        if 'Pass' in sub_pf.columns and 'Fail' in sub_pf.columns:
            sub_pf['Pass_Rate'] = (sub_pf['Pass'] / (sub_pf['Pass'] + sub_pf['Fail'])) * 100
            fig_sub_pf = px.bar(
                sub_pf, x='Subject', y='Pass_Rate',
                title="Pass Rate by Subject (%)",
                color='Pass_Rate',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(apply_chart_style(fig_sub_pf, height=380), use_container_width=True)

    csv_bytes = df_pf.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Pass/Fail Ledger (CSV)", csv_bytes, "pass_fail_ledger.csv", "text/csv")
