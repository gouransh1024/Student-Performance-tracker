"""
Enter & Update Marks Page - Assessment Management with Academic Terms
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.subject import Subject
from models.marks import Marks, display_marks_table
from utils.ui_theme import inject_custom_theme, render_grade_pill, render_sidebar_header

st.set_page_config(
    page_title="Marks & Grading Engine | ApexTracker",
    page_icon="📝",
    layout="wide"
)

inject_custom_theme()
render_sidebar_header()

st.markdown("""
<div style="background: linear-gradient(135deg, #1E1B4B 0%, #4338CA 100%); 
            padding: 1.8rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.8rem;
            box-shadow: 0 10px 20px -5px rgba(67, 56, 202, 0.3);">
    <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">
        📝 Assessment Marks & Grading Engine
    </h1>
    <p style="color: #E0E7FF; font-size: 0.98rem; margin: 0;">
        Record examination scores, assignments, quizzes, and track academic progression across terms.
    </p>
</div>
""", unsafe_allow_html=True)

tab_entry, tab_view, tab_edit, tab_delete = st.tabs([
    "➕ Record New Assessment",
    "📋 Assessment Ledger",
    "✏️ Modify Entry",
    "🗑️ Remove Entry"
])

# Helpers
def get_student_map():
    students = Student.get_all_students()
    return {f"{s[1]} (Roll: {s[5] or s[0]} | Class {s[2]}-{s[3]})": s[0] for s in students} if students else {}

def get_subject_map():
    subjects = Subject.get_all_subjects()
    return {f"{s[1]} (ID: {s[0]})": s[0] for s in subjects} if subjects else {}

# 1. Record New Assessment
with tab_entry:
    student_map = get_student_map()
    subject_map = get_subject_map()

    if not student_map or not subject_map:
        st.warning("⚠️ Both students and subjects must be created before logging marks.")
    else:
        with st.form("enter_marks_form"):
            col1, col2 = st.columns(2)
            with col1:
                selected_st_key = st.selectbox("Select Student *", list(student_map.keys()))
                student_id = student_map[selected_st_key]

                selected_sub_key = st.selectbox("Select Subject *", list(subject_map.keys()))
                subject_id = subject_map[selected_sub_key]

                term_choice = st.selectbox(
                    "Academic Term *",
                    ["Term 1", "Term 2", "Midterm Examination", "Finals", "Summer Session"],
                    index=0
                )

            with col2:
                c2a, c2b = st.columns(2)
                with c2a:
                    obtained = st.number_input("Marks Obtained *", min_value=0, max_value=1000, value=75)
                with c2b:
                    max_score = st.number_input("Maximum Marks *", min_value=1, max_value=1000, value=100)

                assess_date = st.date_input("Assessment Date *", value=date.today(), max_value=date.today())
                assess_type = st.selectbox("Assessment Type *", ["Assignment", "Quiz", "Midterm", "Final", "Project", "Practical"])

            submit_marks = st.form_submit_button("Record Assessment", type="primary", use_container_width=True)

            if submit_marks:
                valid, errors = Marks.validate_marks_data(obtained, max_score, assess_date)
                if valid:
                    success = Marks.add_marks(
                        student_id=student_id,
                        subject_id=subject_id,
                        marks_obtained=obtained,
                        max_marks=max_score,
                        assessment_date=assess_date,
                        assessment_type=assess_type,
                        term=term_choice
                    )
                    if success:
                        pct = Marks.calculate_percentage(obtained, max_score)
                        grd = Marks.calculate_grade(pct)
                        st.success(f"✅ Recorded marks for {selected_st_key.split(' (')[0]} - {selected_sub_key.split(' (')[0]}: {obtained}/{max_score} ({pct:.1f}% • Grade {grd}) [{term_choice}]")
                    else:
                        st.error("Failed to insert marks record into database.")
                else:
                    for e in errors:
                        st.error(f"❌ {e}")

# 2. View All Marks
with tab_view:
    all_records = Marks.get_all_marks()
    if all_records:
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st_filter = st.selectbox("Student:", ["All"] + sorted(list(set(m[1] for m in all_records))))
        with fc2:
            sub_filter = st.selectbox("Subject:", ["All"] + sorted(list(set(m[2] for m in all_records))))
        with fc3:
            type_filter = st.selectbox("Assessment:", ["All"] + sorted(list(set(m[6] for m in all_records))))
        with fc4:
            term_filter = st.selectbox("Term:", ["All"] + sorted(list(set(m[8] for m in all_records if len(m) > 8 and m[8]))))

        filtered = all_records
        if st_filter != "All":
            filtered = [m for m in filtered if m[1] == st_filter]
        if sub_filter != "All":
            filtered = [m for m in filtered if m[2] == sub_filter]
        if type_filter != "All":
            filtered = [m for m in filtered if m[6] == type_filter]
        if term_filter != "All":
            filtered = [m for m in filtered if len(m) > 8 and m[8] == term_filter]

        st.success(f"Displaying {len(filtered)} assessment record(s)")
        display_marks_table(filtered)

        # Export CSV
        df_export = pd.DataFrame([
            {
                "Mark ID": m[0],
                "Student": m[1],
                "Subject": m[2],
                "Marks Obtained": m[3],
                "Max Marks": m[4],
                "Percentage": f"{Marks.calculate_percentage(m[3], m[4]):.1f}%",
                "Grade": Marks.calculate_grade(Marks.calculate_percentage(m[3], m[4])),
                "Date": m[5],
                "Type": m[6],
                "Term": m[8] if len(m) > 8 else "Term 1"
            }
            for m in filtered
        ])

        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Assessment Ledger (CSV)",
            data=csv_bytes,
            file_name=f"marks_ledger_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="secondary"
        )
    else:
        st.info("No assessment records found.")

# 3. Update Marks
with tab_edit:
    all_mk = Marks.get_all_marks()
    if all_mk:
        mk_lookup = {
            f"{m[1]} - {m[2]} ({m[3]}/{m[4]}) [{m[6]}] - {m[5]}": m[0]
            for m in all_mk
        }
        chosen_mk_key = st.selectbox("Choose Entry to Modify:", list(mk_lookup.keys()))
        chosen_mk_id = mk_lookup[chosen_mk_key]
        mk_data = next((m for m in all_mk if m[0] == chosen_mk_id), None)

        if mk_data:
            with st.form("edit_mark_entry_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    new_ob = st.number_input("Marks Obtained *", min_value=0, max_value=1000, value=mk_data[3])
                    new_max = st.number_input("Maximum Marks *", min_value=1, max_value=1000, value=mk_data[4])
                with ec2:
                    curr_date = pd.to_datetime(mk_data[5]).date() if mk_data[5] else date.today()
                    new_date = st.date_input("Assessment Date *", value=curr_date, max_value=date.today())
                    types = ["Assignment", "Quiz", "Midterm", "Final", "Project", "Practical"]
                    curr_type_idx = types.index(mk_data[6]) if mk_data[6] in types else 0
                    new_type = st.selectbox("Assessment Type *", types, index=curr_type_idx)

                term_val = mk_data[8] if len(mk_data) > 8 and mk_data[8] else "Term 1"
                term_choices = ["Term 1", "Term 2", "Midterm Examination", "Finals", "Summer Session"]
                term_idx = term_choices.index(term_val) if term_val in term_choices else 0
                new_term = st.selectbox("Term *", term_choices, index=term_idx)

                save_update = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                if save_update:
                    valid, errs = Marks.validate_marks_data(new_ob, new_max, new_date)
                    if valid:
                        if Marks.update_marks(chosen_mk_id, new_ob, new_max, new_date, new_type, new_term):
                            st.success("✅ Assessment record updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update marks in database.")
                    else:
                        for e in errs:
                            st.error(f"❌ {e}")
    else:
        st.info("No records to modify.")

# 4. Delete Marks
with tab_delete:
    all_mk_del = Marks.get_all_marks()
    if all_mk_del:
        del_lookup = {
            f"{m[1]} - {m[2]} ({m[3]}/{m[4]}) [{m[6]}] - {m[5]}": m[0]
            for m in all_mk_del
        }
        del_key = st.selectbox("Select Entry to Delete:", list(del_lookup.keys()), key="del_mk_select")
        del_id = del_lookup[del_key]

        if st.checkbox(f"Confirm deletion of {del_key}"):
            if st.button("🚨 Delete Entry", type="primary"):
                if Marks.delete_marks(del_id):
                    st.success("✅ Assessment record deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete.")
    else:
        st.info("No records available.")
