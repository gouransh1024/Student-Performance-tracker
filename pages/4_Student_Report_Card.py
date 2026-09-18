"""
Student Report Card Page - Individual & Batch Performance Evaluations
Enhanced with GPA/CGPA, Competency Radar, Attendance Metrics, and Batch Class ZIP Export
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
from utils.ui_theme import (
    inject_custom_theme, get_student_avatar_svg, render_kpi_card, 
    render_grade_pill, render_sidebar_header
)
from utils.chart_theme import create_subject_radar_chart
from utils.pdf_generator import generate_student_report_pdf, generate_class_report_cards_zip

st.set_page_config(
    page_title="Academic Report Cards | ApexTracker",
    page_icon="📋",
    layout="wide"
)

inject_custom_theme()
render_sidebar_header()

st.markdown("""
<div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%); 
            padding: 1.8rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.8rem;
            box-shadow: 0 10px 20px -5px rgba(67, 56, 202, 0.3);">
    <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">
        📋 Academic Evaluation & Report Cards
    </h1>
    <p style="color: #E0E7FF; font-size: 0.98rem; margin: 0;">
        Generate publication-grade PDF report cards, competency profiles, and batch class archives.
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch enrolled students
all_students = Student.get_all_students()
if not all_students:
    st.warning("⚠️ No students found in the database. Please add students first.")
    st.stop()

tab_single, tab_batch = st.tabs([
    "👤 Individual Student Report",
    "📦 Batch Class Report Cards (.ZIP)"
])

# 1. Individual Report Tab
with tab_single:
    col_sel1, col_sel2 = st.columns([2, 1])
    student_options = {
        f"{s[1]} (Roll: {s[5] or s[0]} | Class {s[2]}-{s[3]})": s[0] 
        for s in all_students
    }

    with col_sel1:
        chosen_label = st.selectbox("Select Student Profile:", list(student_options.keys()))
        chosen_id = student_options[chosen_label]

    with col_sel2:
        quick_id_search = st.text_input("Or Quick Find by Roll / ID:", placeholder="e.g. 10A-01")
        if quick_id_search.strip():
            found_st = Student.get_student_by_roll_no(quick_id_search.strip())
            if found_st:
                chosen_id = found_st[0]
                st.caption(f"Loaded: {found_st[1]}")

    student_info = Student.get_student_by_id(chosen_id)
    student_summary = Marks.get_student_summary(chosen_id)
    attendance_summary = Attendance.get_student_attendance_summary(chosen_id)

    if not student_info:
        st.error("Student profile not found.")
        st.stop()

    if student_summary['total_subjects'] == 0:
        st.info(f"ℹ️ No marks logged yet for {student_info[1]}.")
    else:
        # Profile Header with SVG Avatar
        avatar_svg = get_student_avatar_svg(student_info[1], size=75)
        roll_val = student_info[5] if len(student_info) > 5 and student_info[5] else f"ID-{student_info[0]}"
        email_val = student_info[6] if len(student_info) > 6 and student_info[6] else "Not Provided"

        st.markdown(f"""
        <div class="glass-card" style="display: flex; align-items: center; gap: 1.5rem; padding: 1.4rem; margin: 1.2rem 0;">
            <div>{avatar_svg}</div>
            <div style="flex-grow: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                    <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800;">{student_info[1]}</h2>
                    <span style="background: rgba(99, 102, 241, 0.2); color: #818CF8; font-weight: 700; font-size: 0.8rem; 
                                 padding: 3px 10px; border-radius: 9999px;">Roll: {roll_val}</span>
                </div>
                <p style="margin: 0; opacity: 0.85; font-size: 0.92rem;">
                    Class <strong>{student_info[2]}</strong> • Section <strong>{student_info[3]}</strong> • 
                    DOB: <strong>{student_info[4]}</strong> • Email: <strong>{email_val}</strong>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Performance Metric Tiles
        pct = student_summary.get('overall_percentage', 0.0)
        gpa = student_summary.get('gpa', 0.0)
        cgpa = student_summary.get('cgpa', 0.0)
        grd = student_summary.get('overall_grade', 'N/A')
        att_rate = attendance_summary.get('attendance_rate', 0.0)

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            render_kpi_card("Overall Score", f"{pct:.1f}%", f"{student_summary.get('total_marks_obtained', 0)} / {student_summary.get('total_max_marks', 0)}", "🎯", None)
        with k2:
            render_kpi_card("Final Grade", grd, f"Standing: {student_summary.get('pass_fail_status', 'N/A')}", "🏆", None)
        with k3:
            render_kpi_card("GPA (4.0)", f"{gpa:.2f}", "Weighted Scale", "🎓", None)
        with k4:
            render_kpi_card("CGPA (10.0)", f"{cgpa:.2f}", "National Metric", "⭐", None)
        with k5:
            delta_type = "positive" if att_rate >= 75 else "negative"
            render_kpi_card("Attendance", f"{att_rate:.1f}%", f"{attendance_summary.get('present_days', 0)}/{attendance_summary.get('total_days', 0)} Days", "📅", "Good Standing" if att_rate >= 75 else "Low Attendance", delta_type)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Competency Radar Profile & Subject Breakdown
        col_c1, col_c2 = st.columns([1, 1])

        with col_c1:
            st.markdown("### 🕸️ Competency Radar Profile")
            st.plotly_chart(create_subject_radar_chart(student_summary.get('subject_details', [])), use_container_width=True)

        with col_c2:
            st.markdown("### 📚 Subject Assessment Ledger")
            subj_rows = []
            for s in student_summary.get('subject_details', []):
                subj_rows.append({
                    "Subject": s.get('subject'),
                    "Score": f"{s.get('marks_obtained')} / {s.get('max_marks')}",
                    "Percentage": f"{s.get('percentage', 0):.1f}%",
                    "Grade": s.get('grade', 'N/A'),
                    "Term": s.get('term', 'Term 1'),
                    "Type": s.get('assessment_type', 'Exam')
                })
            df_subj = pd.DataFrame(subj_rows)
            st.dataframe(df_subj, use_container_width=True, hide_index=True)

            # Strengths & Weaknesses
            details = student_summary.get('subject_details', [])
            if details:
                best_sub = max(details, key=lambda x: x.get('percentage', 0))
                lowest_sub = min(details, key=lambda x: x.get('percentage', 0))
                st.markdown(f"🌟 **Top Discipline:** {best_sub.get('subject')} ({best_sub.get('percentage'):.1f}%)")
                st.markdown(f"🔍 **Development Focus:** {lowest_sub.get('subject')} ({lowest_sub.get('percentage'):.1f}%)")

        st.markdown("---")

        # PDF & CSV Export Row
        st.markdown("### 📥 Official Transcript Export")
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            pdf_bytes = generate_student_report_pdf(student_summary, student_info, attendance_summary)
            clean_st_name = student_info[1].replace(' ', '_')
            st.download_button(
                label=f"📄 Download Official Report Card (PDF)",
                data=pdf_bytes,
                file_name=f"{clean_st_name}_Report_Card.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        with c_exp2:
            csv_bytes = df_subj.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Download Subject Summary (CSV)",
                data=csv_bytes,
                file_name=f"{clean_st_name}_Subjects.csv",
                mime="text/csv",
                type="secondary",
                use_container_width=True
            )

# 2. Batch ZIP Export Tab
with tab_batch:
    st.subheader("📦 Generate Batch Class Report Cards (.ZIP)")
    st.caption("Bundle individual, official PDF report cards for all enrolled students in a cohort into a single compressed ZIP archive.")

    unique_classes = Student.get_unique_classes()
    if not unique_classes:
        st.info("No class groups available.")
    else:
        bc1, bc2 = st.columns(2)
        with bc1:
            batch_class = st.selectbox("Select Target Class:", unique_classes, key="batch_class_picker")
        with bc2:
            avail_sections = ["All"] + list(set(s[3] for s in Student.get_students_by_class(batch_class)))
            batch_section = st.selectbox("Select Target Section:", avail_sections, key="batch_sec_picker")

        sec_param = None if batch_section == "All" else batch_section
        targeted_students = Student.get_students_by_class(batch_class, sec_param)

        st.markdown(f"**Targeted Cohort:** Class {batch_class} (Section: {batch_section}) &bull; **{len(targeted_students)} Students**")

        if len(targeted_students) > 0:
            with st.spinner("Compiling batch PDF archive..."):
                try:
                    zip_data = generate_class_report_cards_zip(batch_class, sec_param)
                    if zip_data:
                        st.success(f"✅ Archive built successfully ({len(zip_data) // 1024} KB)")
                        st.download_button(
                            label=f"📦 Download Class {batch_class} Report Cards (.ZIP)",
                            data=zip_data,
                            file_name=f"Class_{batch_class}_{batch_section}_Report_Cards.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.warning("No PDF report cards could be compiled for this cohort.")
                except Exception as zip_err:
                    st.error(f"Error compiling ZIP archive: {zip_err}")
        else:
            st.info("No students found in this cohort selection.")
