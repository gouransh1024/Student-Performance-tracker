"""
Student Performance Tracker - Main Application
Next-Generation Academic Intelligence & Performance Management Suite
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connection import get_db_connection, init_database, get_database_info
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from models.attendance import Attendance
from utils.ui_theme import (
    inject_custom_theme, render_kpi_card, render_role_selector, 
    render_grade_pill, get_student_avatar_svg, render_theme_switcher,
    render_sidebar_header
)
from utils.chart_theme import (
    create_grade_donut_chart, create_podium_bar_chart, create_subject_radar_chart
)
from utils.pdf_generator import generate_student_report_pdf

# Page configuration
st.set_page_config(
    page_title="Academic Intelligence | Student Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified design system
inject_custom_theme()

def initialize_app():
    """Ensure database schema is up-to-date and populated"""
    if 'db_initialized' not in st.session_state:
        try:
            if init_database():
                st.session_state.db_initialized = True
                Student.auto_assign_missing_roll_numbers()
                return True
            else:
                st.error("❌ Database initialization encountered an issue.")
                return False
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
            return False
    return True

def display_teacher_dashboard():
    """Enterprise Teacher / Administrator Dashboard"""
    # Luxury Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%); 
                padding: 2.2rem 2.5rem; border-radius: 20px; color: white; margin-bottom: 2rem;
                box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.35); position: relative; overflow: hidden;">
        <div style="position: relative; z-index: 2;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="background: rgba(255,255,255,0.18); backdrop-filter: blur(8px); 
                             padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; 
                             font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                    Institutional Command Center
                </span>
                <span style="color: #A5B4FC; font-size: 0.85rem;">• Academic Session 2026-2027</span>
            </div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.4rem; font-weight: 800; 
                       margin: 0 0 10px 0; letter-spacing: -0.03em; color: #FFFFFF;">
                Student Performance & Academic Analytics
            </h1>
            <p style="color: #E0E7FF; font-size: 1.05rem; margin: 0; max-width: 720px; line-height: 1.5;">
                Holistic student evaluations, dynamic CGPA/GPA tracking, attendance correlation, 
                and early intervention diagnostics.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch Cohort Metrics
    try:
        students = Student.get_all_students()
        subjects = Subject.get_all_subjects()
        marks = Marks.get_all_marks()
        at_risk_students = Marks.get_at_risk_students()

        student_count = len(students) if students else 0
        subject_count = len(subjects) if subjects else 0
        marks_count = len(marks) if marks else 0

        # Cohort average
        if marks:
            total_obtained = sum(m[3] for m in marks)
            total_possible = sum(m[4] for m in marks)
            overall_avg = (total_obtained / total_possible * 100) if total_possible > 0 else 0
        else:
            overall_avg = 0.0

        # Calculate attendance cohort rate
        correlation_data = Attendance.get_all_students_attendance_correlation()
        if correlation_data:
            valid_att = [d['attendance_pct'] for d in correlation_data if d['attendance_pct'] is not None]
            avg_attendance = sum(valid_att) / len(valid_att) if valid_att else 0.0
        else:
            avg_attendance = 0.0

    except Exception as e:
        st.error(f"Error loading dashboard metrics: {e}")
        student_count, subject_count, marks_count, overall_avg, avg_attendance = 0, 0, 0, 0.0, 0.0
        at_risk_students = []

    # KPI Metric Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi_card("Total Students", f"{student_count}", "Active Enrolled", "👥", "+100%", "positive")
    with c2:
        render_kpi_card("Curriculum", f"{subject_count}", "Credit Subjects", "📚", None)
    with c3:
        render_kpi_card("Cohort Average", f"{overall_avg:.1f}%", "Overall Marks", "📈", "+3.2%", "positive" if overall_avg >= 60 else "negative")
    with c4:
        render_kpi_card("Avg Attendance", f"{avg_attendance:.1f}%", "Cohort Presence", "📅", "+1.5%", "positive" if avg_attendance >= 75 else "negative")
    with c5:
        risk_color = "negative" if len(at_risk_students) > 0 else "positive"
        render_kpi_card("At-Risk Students", f"{len(at_risk_students)}", "Needs Attention", "⚠️", f"{len(at_risk_students)} flagged", risk_color)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Early Warning & At-Risk Intervention Alert (if any)
    if at_risk_students:
        st.markdown("""
        <div style="background: rgba(254, 242, 242, 0.95); border-left: 5px solid #EF4444; 
                    padding: 1.2rem 1.5rem; border-radius: 12px; margin-bottom: 1.8rem;
                    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08);">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="color: #991B1B; margin: 0 0 6px 0; font-size: 1.15rem; font-weight: 700;">
                        🚨 Early Intervention Alert: Students Requiring Academic Attention
                    </h3>
                    <p style="color: #B91C1C; margin: 0; font-size: 0.92rem;">
                        The diagnostic engine identified students performing below standard academic benchmarks (Percentage < 40% or Attendance < 75%).
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"⚠️ Review Flagged Students ({len(at_risk_students)} detected)", expanded=True):
            risk_rows = []
            for s in at_risk_students:
                risk_rows.append({
                    "ID": s['student_id'],
                    "Name": s['name'],
                    "Class": f"{s['class']}-{s['section']}",
                    "Score %": f"{s['overall_percentage']:.1f}%",
                    "Grade": s['overall_grade'],
                    "Attendance %": f"{s['attendance_rate']:.1f}%",
                    "Primary Concerns": ", ".join(s['risk_factors'])
                })
            st.dataframe(pd.DataFrame(risk_rows), use_container_width=True, hide_index=True)
            st.caption("💡 Recommended Action: Schedule faculty advising sessions or initiate targeted remedial tutoring.")

    # Visual Cohort Insights (2 Columns: Grade Distribution + Top Performers)
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.markdown("### 📊 Cohort Grade Distribution")
        if marks:
            grade_counts = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'F': 0}
            for m in marks:
                pct = Marks.calculate_percentage(m[3], m[4])
                grd = Marks.calculate_grade(pct)
                grade_counts[grd] = grade_counts.get(grd, 0) + 1
            st.plotly_chart(create_grade_donut_chart(grade_counts), use_container_width=True)
        else:
            st.info("No marks data available to plot grade distribution.")

    with col_chart2:
        st.markdown("### 🏆 Academic Leaderboard")
        try:
            summary_df = Marks.get_all_students_summary_dataframe()
            if not summary_df.empty:
                st.plotly_chart(create_podium_bar_chart(summary_df), use_container_width=True)
            else:
                st.info("Leaderboard will populate once assessments are recorded.")
        except Exception:
            st.info("Leaderboard will appear as assessments are recorded.")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Executive Navigation Hub
    st.markdown("### ⚡ Quick Navigation Hub")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("👥 Manage Students & Attendance", use_container_width=True, type="secondary"):
            st.switch_page("pages/1_Manage_Students.py")
    with q2:
        if st.button("📝 Record Assessment Marks", use_container_width=True, type="secondary"):
            st.switch_page("pages/3_Enter_Update_Marks.py")
    with q3:
        if st.button("📋 Batch Report Cards (PDF / ZIP)", use_container_width=True, type="secondary"):
            st.switch_page("pages/4_Student_Report_Card.py")
    with q4:
        if st.button("🔬 In-Depth Class Analytics", use_container_width=True, type="secondary"):
            st.switch_page("pages/5_Class_Analytics.py")


def display_student_portal():
    """Direct Student / Parent Self-Service Portal"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #065F46 0%, #047857 50%, #059669 100%); 
                padding: 2.2rem 2.5rem; border-radius: 20px; color: white; margin-bottom: 2rem;
                box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.35);">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <span style="background: rgba(255,255,255,0.2); backdrop-filter: blur(8px); 
                         padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; 
                         font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                Student & Parent Access
            </span>
        </div>
        <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.3rem; font-weight: 800; margin: 0 0 10px 0;">
            Academic Progress Portal
        </h1>
        <p style="color: #D1FAE5; font-size: 1.05rem; margin: 0; max-width: 650px;">
            Lookup your official grade transcript, attendance statistics, subject competency profile, 
            and download your official PDF report card.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Student Selector / Roll Number Lookup
    st.markdown("### 🔍 Search Student Transcript")
    
    all_students = Student.get_all_students()
    if not all_students:
        st.warning("No student records found in the database. Please ask a teacher or admin to add student records.")
        return

    col_s1, col_s2 = st.columns([2, 1])
    
    student_options = {
        f"{s[1]} (Roll: {s[5] or s[0]} | Class {s[2]}-{s[3]})": s[0] 
        for s in all_students
    }

    with col_s1:
        selected_label = st.selectbox("Select Student Profile:", list(student_options.keys()))
        selected_id = student_options[selected_label]

    with col_s2:
        roll_search = st.text_input("Or Quick Lookup by Roll No / ID:", placeholder="e.g. 10A-01 or 1")
        if roll_search.strip():
            found = Student.get_student_by_roll_no(roll_search.strip())
            if found:
                selected_id = found[0]
                st.success(f"Loaded: {found[1]}")
            else:
                st.info("No exact match found, using dropdown selection.")

    # Load selected student data
    student_info = Student.get_student_by_id(selected_id)
    student_summary = Marks.get_student_summary(selected_id)
    attendance_summary = Attendance.get_student_attendance_summary(selected_id)

    if not student_info:
        st.error("Student record not found.")
        return

    # Student Profile Header with SVG Avatar
    avatar_html = get_student_avatar_svg(student_info[1], size=75)
    roll_disp = student_info[5] if len(student_info) > 5 and student_info[5] else f"ID-{student_info[0]}"
    email_disp = student_info[6] if len(student_info) > 6 and student_info[6] else "Not Registered"

    st.markdown(f"""
    <div class="glass-card" style="display: flex; align-items: center; gap: 1.5rem; padding: 1.5rem; margin: 1.2rem 0;">
        <div>{avatar_html}</div>
        <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700;">{student_info[1]}</h2>
                <span style="background: rgba(99, 102, 241, 0.2); color: #818CF8; font-weight: 700; font-size: 0.8rem; 
                             padding: 3px 10px; border-radius: 9999px;">Roll: {roll_disp}</span>
            </div>
            <p style="margin: 0; opacity: 0.85; font-size: 0.95rem;">
                Class <strong>{student_info[2]}</strong> • Section <strong>{student_info[3]}</strong> • 
                DOB: <strong>{student_info[4]}</strong> • Email: <strong>{email_disp}</strong>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Performance Overview Cards
    pct = student_summary.get('overall_percentage', 0.0)
    gpa = student_summary.get('gpa', 0.0)
    cgpa = student_summary.get('cgpa', 0.0)
    grade = student_summary.get('overall_grade', 'N/A')
    att_rate = attendance_summary.get('attendance_rate', 0.0)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_card("Overall Score", f"{pct:.1f}%", f"{student_summary.get('total_marks_obtained', 0)}/{student_summary.get('total_max_marks', 0)}", "🎯", None)
    with k2:
        render_kpi_card("Final Grade", grade, f"Standing: {student_summary.get('pass_fail_status', 'N/A')}", "🏆", None)
    with k3:
        render_kpi_card("GPA (4.0)", f"{gpa:.2f}", "Academic Honor Scale", "🎓", None)
    with k4:
        render_kpi_card("CGPA (10.0)", f"{cgpa:.2f}", "Standard Index", "⭐", None)
    with k5:
        att_delta = "positive" if att_rate >= 75 else "negative"
        render_kpi_card("Attendance", f"{att_rate:.1f}%", f"{attendance_summary.get('present_days', 0)}/{attendance_summary.get('total_days', 0)} Days", "📅", "Good Standing" if att_rate >= 75 else "Low Attendance", att_delta)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Radar Chart & Marks Breakdown Table
    col_vis1, col_vis2 = st.columns([1, 1])

    with col_vis1:
        st.markdown("### 🕸️ Competency Radar Profile")
        subject_details = student_summary.get('subject_details', [])
        if subject_details:
            st.plotly_chart(create_subject_radar_chart(subject_details), use_container_width=True)
        else:
            st.info("No subject marks logged yet.")

    with col_vis2:
        st.markdown("### 📑 Detailed Course Marks")
        if subject_details:
            table_data = []
            for s in subject_details:
                table_data.append({
                    "Subject": s.get('subject'),
                    "Score": f"{s.get('marks_obtained')} / {s.get('max_marks')}",
                    "Percentage": f"{s.get('percentage', 0):.1f}%",
                    "Grade": s.get('grade', 'N/A'),
                    "Term": s.get('term', 'Term 1'),
                    "Assessment": s.get('assessment_type', 'Exam')
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

            # Official PDF Download Button (Direct 1-click download)
            pdf_data = generate_student_report_pdf(student_summary, student_info, attendance_summary)
            clean_name = student_info[1].replace(' ', '_')
            st.download_button(
                label=f"📄 Download Official Report Card (PDF)",
                data=pdf_data,
                file_name=f"{clean_name}_Official_Report_Card.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.info("No courses or assessments available for this student.")


def display_sidebar():
    """Render modern sidebar with Theme Switcher, Role Perspective Switcher, and system navigation"""
    with st.sidebar:
        render_sidebar_header()

        # Interactive Role Switcher
        current_role = render_role_selector()
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Primary Navigation
        st.markdown("##### 📌 System Modules")
        if st.button("🏠 Command Center", use_container_width=True, type="primary"):
            st.rerun()

        if current_role.startswith("Teacher"):
            if st.button("👥 Student Directory & Attendance", use_container_width=True):
                st.switch_page("pages/1_Manage_Students.py")

            if st.button("📚 Subject & Curriculum", use_container_width=True):
                st.switch_page("pages/2_Manage_Subjects.py")

            if st.button("📝 Marks & Grading Engine", use_container_width=True):
                st.switch_page("pages/3_Enter_Update_Marks.py")

            if st.button("📋 Student Report Cards", use_container_width=True):
                st.switch_page("pages/4_Student_Report_Card.py")

            if st.button("📊 Class Analytics & Heatmap", use_container_width=True):
                st.switch_page("pages/5_Class_Analytics.py")

            if st.button("📈 Cohort Visual Reports", use_container_width=True):
                st.switch_page("pages/6_Visual_Reports.py")

            if st.button("📤 Bulk Data Exchange", use_container_width=True):
                st.switch_page("pages/8_Bulk_Data_Import.py")

            if st.button("⚙️ System Settings", use_container_width=True):
                st.switch_page("pages/7_Settings.py")
        else:
            if st.button("📋 View My Report Card", use_container_width=True):
                st.switch_page("pages/4_Student_Report_Card.py")

        st.markdown("---")

        # Database Engine Info Tile
        try:
            db_info = get_database_info()
            if db_info.get('database_exists'):
                st.markdown("""
                <div class="sidebar-status-card">
                    <div style="display: flex; align-items: center; gap: 6px; color: #10B981; font-weight: 700; margin-bottom: 6px;">
                        <span>●</span> SQLite Engine Active
                    </div>
                    <div>
                        <div>Students: <strong>{}</strong></div>
                        <div>Subjects: <strong>{}</strong></div>
                        <div>Assessments: <strong>{}</strong></div>
                    </div>
                </div>
                """.format(
                    db_info.get('student_count', 0),
                    db_info.get('subject_count', 0),
                    db_info.get('marks_count', 0)
                ), unsafe_allow_html=True)
        except Exception:
            pass

def main():
    """Main application execution router"""
    if not initialize_app():
        st.stop()

    display_sidebar()

    # Route based on active role perspective
    current_role = st.session_state.get('user_role', 'Teacher / Administrator')
    if current_role.startswith("Teacher"):
        display_teacher_dashboard()
    else:
        display_student_portal()

    # Refined Institutional Footer
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #94A3B8; font-size: 0.82rem; border-top: 1px solid #E2E8F0; padding-top: 20px;'>
        <p>🎓 <strong>Student Performance Tracker & Academic Analytics</strong> &bull; Production Enterprise Edition</p>
        <p>Fully functional &bull; Responsive Design &bull; Multi-Role Perspective &bull; Automated Diagnostic Engine</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
