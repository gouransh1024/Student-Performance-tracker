"""
Manage Students & Attendance - Comprehensive Student Directory
Enhanced with Roll Numbers, Emails, Avatars, and Quick Attendance Logging
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.attendance import Attendance
from utils.ui_theme import inject_custom_theme, get_student_avatar_svg, render_kpi_card, render_sidebar_header

st.set_page_config(
    page_title="Manage Students & Attendance | ApexTracker",
    page_icon="👥",
    layout="wide"
)

# Apply global styling
inject_custom_theme()
render_sidebar_header()

# Header Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #1E1B4B 0%, #3730A3 100%); 
            padding: 1.8rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.8rem;
            box-shadow: 0 10px 20px -5px rgba(55, 48, 163, 0.3);">
    <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">
        👥 Student Directory & Attendance Management
    </h1>
    <p style="color: #C7D2FE; font-size: 0.98rem; margin: 0;">
        Manage student biographical records, assign roll numbers and emails, and record daily cohort attendance.
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation tabs
tab_view, tab_add, tab_att, tab_edit, tab_delete = st.tabs([
    "📋 Student Directory", 
    "➕ Enroll New Student", 
    "📅 Quick Attendance Logger", 
    "✏️ Edit Records", 
    "🗑️ Delete Student"
])

# 1. Student Directory Tab
with tab_view:
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        search_query = st.text_input("🔍 Search by Name, Roll No, or Email:", placeholder="Type to filter...")
    with col_f2:
        classes = ["All"] + Student.get_unique_classes()
        filter_class = st.selectbox("Class Filter:", classes)
    with col_f3:
        sections = ["All"] + Student.get_unique_sections()
        filter_section = st.selectbox("Section Filter:", sections)

    students_raw = Student.search_students(
        search_term=search_query,
        class_filter="" if filter_class == "All" else filter_class,
        section_filter="" if filter_section == "All" else filter_section
    )

    if students_raw:
        st.success(f"Found {len(students_raw)} enrolled student(s)")
        
        df = pd.DataFrame(students_raw, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Roll No', 'Email', 'Enrolled On'])
        df['DOB'] = pd.to_datetime(df['DOB']).dt.strftime('%Y-%m-%d')
        df['Enrolled On'] = pd.to_datetime(df['Enrolled On']).dt.strftime('%Y-%m-%d')

        st.dataframe(
            df[['ID', 'Roll No', 'Name', 'Class', 'Section', 'DOB', 'Email', 'Enrolled On']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Roll No": st.column_config.TextColumn("Roll No", width="small"),
                "Name": st.column_config.TextColumn("Full Name", width="medium"),
                "Class": st.column_config.TextColumn("Class", width="small"),
                "Section": st.column_config.TextColumn("Sec", width="small"),
                "DOB": st.column_config.TextColumn("DOB", width="medium"),
                "Email": st.column_config.TextColumn("Email Address", width="medium"),
                "Enrolled On": st.column_config.TextColumn("Enrolled", width="small")
            }
        )

        # CSV Export
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Students (CSV)",
            data=csv_bytes,
            file_name=f"students_export_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="secondary"
        )
    else:
        st.info("No students found matching your criteria.")

# 2. Add Student Tab
with tab_add:
    st.subheader("➕ Enroll New Student")
    with st.form("add_student_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Full Name *", placeholder="e.g. Liam Smith")
            new_class = st.text_input("Class / Grade *", placeholder="e.g. 10")
            new_roll = st.text_input("Roll Number (Optional)", placeholder="e.g. 10A-11 (Leave empty to auto-assign)")
        with c2:
            new_section = st.text_input("Section *", placeholder="e.g. A")
            new_dob = st.date_input("Date of Birth *", value=date.today().replace(year=date.today().year - 15), max_value=date.today())
            new_email = st.text_input("Student / Parent Email (Optional)", placeholder="e.g. student@school.edu")

        submit_add = st.form_submit_button("Enroll Student", type="primary", use_container_width=True)
        if submit_add:
            is_valid, errors = Student.validate_student_data(new_name, new_class, new_section, new_dob, new_roll, new_email)
            if is_valid:
                success = Student.add_student(new_name, new_class, new_section, new_dob, new_roll, new_email)
                if success:
                    st.success(f"✅ Successfully enrolled {new_name} in Class {new_class}-{new_section}!")
                    st.rerun()
                else:
                    st.error("Failed to enroll student into database.")
            else:
                for err in errors:
                    st.error(f"❌ {err}")

# 3. Quick Attendance Logger Tab
with tab_att:
    st.subheader("📅 Class Attendance Logger")
    st.caption("Record daily attendance for an entire classroom with one click.")

    all_classes = Student.get_unique_classes()
    if not all_classes:
        st.warning("Please add students and classes first.")
    else:
        att_c1, att_c2, att_c3 = st.columns([1, 1, 1])
        with att_c1:
            selected_att_class = st.selectbox("Select Class:", all_classes, key="att_class_sel")
        with att_c2:
            sections_for_class = ["All"] + list(set(s[3] for s in Student.get_students_by_class(selected_att_class)))
            selected_att_sec = st.selectbox("Select Section:", sections_for_class, key="att_sec_sel")
        with att_c3:
            att_date = st.date_input("Attendance Date:", value=date.today(), max_value=date.today(), key="att_date_sel")

        sec_filter = None if selected_att_sec == "All" else selected_att_sec
        class_students = Student.get_students_by_class(selected_att_class, sec_filter)

        if not class_students:
            st.info(f"No students found in Class {selected_att_class} (Section {selected_att_sec})")
        else:
            st.markdown(f"**Marking Attendance for {len(class_students)} Students on {att_date.strftime('%B %d, %Y')}:**")

            with st.form("batch_attendance_form"):
                attendance_inputs = {}
                cols = st.columns(2)
                for idx, st_item in enumerate(class_students):
                    sid, sname, scls, ssec, sroll = st_item[0], st_item[1], st_item[2], st_item[3], st_item[4]
                    roll_label = f"[{sroll}] " if sroll else ""
                    with cols[idx % 2]:
                        attendance_inputs[sid] = st.radio(
                            f"{roll_label}{sname} ({scls}-{ssec})",
                            options=["Present", "Absent", "Late", "Excused"],
                            horizontal=True,
                            key=f"att_radio_{sid}_{att_date}"
                        )

                save_att = st.form_submit_button("💾 Submit Daily Attendance", type="primary", use_container_width=True)
                if save_att:
                    saved_count = 0
                    for sid, status in attendance_inputs.items():
                        if Attendance.mark_attendance(sid, att_date, status):
                            saved_count += 1
                    st.success(f"✅ Successfully logged attendance for {saved_count} / {len(class_students)} students on {att_date}!")

# 4. Edit Student Tab
with tab_edit:
    st.subheader("✏️ Edit Student Profile")
    all_sts = Student.get_all_students()
    if all_sts:
        st_lookup = {f"{s[1]} (Roll: {s[5] or s[0]} | Class {s[2]}-{s[3]})": s[0] for s in all_sts}
        chosen_key = st.selectbox("Choose Student to Edit:", list(st_lookup.keys()), key="edit_picker")
        chosen_id = st_lookup[chosen_key]
        curr_data = Student.get_student_by_id(chosen_id)

        if curr_data:
            with st.form("edit_student_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    edit_name = st.text_input("Full Name *", value=curr_data[1])
                    edit_class = st.text_input("Class *", value=curr_data[2])
                    edit_roll = st.text_input("Roll Number", value=curr_data[5] or "")
                with ec2:
                    edit_sec = st.text_input("Section *", value=curr_data[3])
                    curr_dob = pd.to_datetime(curr_data[4]).date() if curr_data[4] else date.today()
                    edit_dob = st.date_input("Date of Birth *", value=curr_dob, max_value=date.today())
                    edit_email = st.text_input("Email", value=curr_data[6] or "")

                save_edit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                if save_edit:
                    valid, errs = Student.validate_student_data(edit_name, edit_class, edit_sec, edit_dob, edit_roll, edit_email)
                    if valid:
                        if Student.update_student(chosen_id, edit_name, edit_class, edit_sec, edit_dob, edit_roll, edit_email):
                            st.success(f"✅ Updated details for {edit_name}!")
                            st.rerun()
                        else:
                            st.error("Failed to update record.")
                    else:
                        for err in errs:
                            st.error(f"❌ {err}")
    else:
        st.info("No students enrolled yet.")

# 5. Delete Student Tab
with tab_delete:
    st.subheader("🗑️ Delete Student")
    st.warning("⚠️ Deleting a student permanently removes all their biographical details, marks, and attendance logs.")
    all_sts_del = Student.get_all_students()
    if all_sts_del:
        del_lookup = {f"{s[1]} (Roll: {s[5] or s[0]} | Class {s[2]}-{s[3]})": s[0] for s in all_sts_del}
        del_key = st.selectbox("Select Student to Remove:", list(del_lookup.keys()), key="del_picker")
        del_id = del_lookup[del_key]

        confirm_del = st.checkbox(f"I understand this action is irreversible and permanently removes this record.")
        if confirm_del:
            if st.button("🚨 Permanently Delete Student", type="primary"):
                if Student.delete_student(del_id):
                    st.success("✅ Student and associated academic history deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete student.")
    else:
        st.info("No students available.")
