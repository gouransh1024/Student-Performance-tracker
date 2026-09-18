"""
Manage Subjects Page - Academic Curriculum Configuration
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.subject import Subject, display_subjects_table, subject_form
from utils.ui_theme import inject_custom_theme, render_sidebar_header

st.set_page_config(
    page_title="Manage Subjects | ApexTracker",
    page_icon="📚",
    layout="wide"
)

inject_custom_theme()
render_sidebar_header()

st.markdown("""
<div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
            padding: 1.8rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.8rem;
            box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.3);">
    <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">
        📚 Curriculum & Subject Catalog
    </h1>
    <p style="color: #94A3B8; font-size: 0.98rem; margin: 0;">
        Configure academic disciplines, core subject offerings, and elective modules.
    </p>
</div>
""", unsafe_allow_html=True)

tab_list, tab_add, tab_quick, tab_manage = st.tabs([
    "📋 Subject Catalog",
    "➕ Add New Subject",
    "🚀 Rapid Curriculum Builder",
    "✏️ Edit & Remove"
])

with tab_list:
    search_sub = st.text_input("🔍 Search Subject:", placeholder="Filter by subject title...")
    if search_sub.strip():
        subjects_data = Subject.search_subjects(search_sub.strip())
    else:
        subjects_data = Subject.get_all_subjects()

    if subjects_data:
        st.success(f"Total Subjects Registered: {len(subjects_data)}")
        df = pd.DataFrame(subjects_data, columns=['ID', 'Subject Name', 'Created On'])
        df['Created On'] = pd.to_datetime(df['Created On']).dt.strftime('%Y-%m-%d')
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Subject Name": st.column_config.TextColumn("Subject Title", width="large"),
                "Created On": st.column_config.TextColumn("Created Date", width="medium")
            }
        )

        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Subject List (CSV)",
            data=csv_bytes,
            file_name=f"curriculum_subjects_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="secondary"
        )
    else:
        st.info("No subjects found.")

with tab_add:
    st.subheader("➕ Register New Subject")
    subject_form(form_type="Add")

with tab_quick:
    st.subheader("🚀 Quick-Add Standard Academic Disciplines")
    st.caption("One-click provisioning of standard high school and undergraduate subjects.")

    stem_subjects = ["Advanced Mathematics", "Calculus & Statistics", "Physics Honors", "Organic Chemistry", "Cellular Biology", "Computer Science"]
    humanities = ["World Literature", "Global History", "Macroeconomics", "Environmental Science", "Psychology", "Fine Arts"]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 🔬 STEM Disciplines")
        for subj in stem_subjects:
            if st.button(f"Add {subj}", key=f"quick_{subj}"):
                if Subject.add_subject(subj):
                    st.success(f"✅ Registered {subj}!")
                    st.rerun()
                else:
                    st.warning(f"'{subj}' already exists or couldn't be added.")

    with c2:
        st.markdown("##### 🏛️ Humanities & Social Sciences")
        for subj in humanities:
            if st.button(f"Add {subj}", key=f"quick_{subj}"):
                if Subject.add_subject(subj):
                    st.success(f"✅ Registered {subj}!")
                    st.rerun()
                else:
                    st.warning(f"'{subj}' already exists or couldn't be added.")

with tab_manage:
    st.subheader("✏️ Edit or Remove Subject")
    subjects = Subject.get_all_subjects()
    if subjects:
        sub_opts = {f"{s[1]} (ID: {s[0]})": s[0] for s in subjects}
        selected_key = st.selectbox("Select Subject:", list(sub_opts.keys()))
        selected_id = sub_opts[selected_key]
        sub_info = Subject.get_subject_by_id(selected_id)

        if sub_info:
            col_e, col_d = st.columns(2)
            with col_e:
                st.markdown("##### Modify Subject Name")
                with st.form("edit_subject_form"):
                    renamed = st.text_input("Updated Subject Name:", value=sub_info[1])
                    if st.form_submit_button("Save Subject Name", type="primary"):
                        valid, errs = Subject.validate_subject_data(renamed, check_duplicate=True, exclude_id=selected_id)
                        if valid:
                            if Subject.update_subject(selected_id, renamed):
                                st.success("✅ Subject renamed successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update.")
                        else:
                            for e in errs:
                                st.error(f"❌ {e}")

            with col_d:
                st.markdown("##### Danger Zone")
                st.warning(f"Deleting '{sub_info[1]}' permanently deletes all associated assessment marks.")
                if st.checkbox(f"Confirm deletion of {sub_info[1]}"):
                    if st.button("🚨 Delete Subject", type="primary"):
                        if Subject.delete_subject(selected_id):
                            st.success(f"Subject deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
    else:
        st.info("No subjects to modify.")
