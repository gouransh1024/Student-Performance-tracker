"""
Settings Page - Application configuration and preferences (SQLite version)
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ✅ Correct SQLite imports
from db.connection import get_db_connection, init_database, get_database_info, initialize_sample_data, execute_query
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from utils.ui_theme import inject_custom_theme, render_sidebar_header, get_current_theme
from utils.data_management import (
    get_data_summary, reset_to_sample_data, delete_all_data,
    delete_sample_data, is_sample_data_present, get_sample_data_info
)

st.set_page_config(
    page_title="Settings | ApexTracker",
    page_icon="⚙️",
    layout="wide"
)

inject_custom_theme()

st.title("⚙️ Application Settings")
st.markdown("Configure application preferences and manage system data")

# Sidebar for settings categories
with st.sidebar:
    render_sidebar_header()
    st.subheader("Settings Categories")

    settings_category = st.radio(
        "Choose Category:",
        [
            "Database Management",
            "Data Import/Export", 
            "System Information",
            "Application Preferences",
            "Backup & Restore"
        ]
    )

# Main content area
if settings_category == "Database Management":
    st.subheader("🗄️ Database Management")

    # Database status
    st.markdown("### Database Status")

    try:
        # Test database connection
        db_info = get_database_info()
        test_students = Student.get_all_students()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Database connection is working")
            st.info(f"**Database:** SQLite")
            st.info(f"**Location:** {db_info.get('database_path', 'Unknown')}")
            
        with col2:
            db_size_mb = db_info.get('database_size', 0) / (1024 * 1024) if db_info.get('database_size', 0) > 0 else 0
            st.metric("Database Size", f"{db_size_mb:.2f} MB")

        # Display basic statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            student_count = db_info.get('student_count', 0)
            st.metric("Total Students", student_count)

        with col2:
            subject_count = db_info.get('subject_count', 0)
            st.metric("Total Subjects", subject_count)

        with col3:
            marks_count = db_info.get('marks_count', 0)
            st.metric("Total Marks", marks_count)

    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")

    st.markdown("---")

    # Database operations
    st.markdown("### Database Operations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Reinitialize Database")
        st.warning("⚠️ This will recreate all tables and add sample data")

        if st.button("🔄 Reinitialize Database"):
            with st.spinner("Reinitializing database..."):
                try:
                    if init_database():
                        st.success("✅ Database reinitialized successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to reinitialize database")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with col2:
        st.markdown("#### Add Sample Data")
        st.info("Add sample students, subjects, and marks if database is empty")

        if st.button("📝 Add Sample Data"):
            with st.spinner("Adding sample data..."):
                try:
                    if initialize_sample_data():
                        st.success("✅ Sample data added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add sample data")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown("---")

    # Student Data Management
    st.markdown("### Student Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Delete Selected Students")
        st.warning("⚠️ This will remove selected students and all their associated marks")
        
        # Get current students for selection
        try:
            students = Student.get_all_students()
            
            if students and len(students) > 0:
                st.info(f"📊 Current data: {len(students)} students")
                
                # Add selection column
                if 'selected_students' not in st.session_state:
                    st.session_state.selected_students = []
                
                # Select all checkbox
                select_all = st.checkbox("Select All Students", key="select_all_students")
                
                if select_all:
                    st.warning(f"⚠️ You are about to select ALL {len(students)} students for deletion!")
                    st.session_state.selected_students = [str(student[0]) for student in students]
                else:
                    # Show individual student selection
                    st.markdown("**Select students to delete:**")
                    
                    # Create columns for better layout
                    cols = st.columns(2)
                    for i, student in enumerate(students):
                        col_idx = i % 2
                        with cols[col_idx]:
                            student_id = str(student[0])
                            student_name = student[1]
                            student_class = student[2]
                            student_section = student[3]
                            
                            is_selected = student_id in st.session_state.selected_students
                            if st.checkbox(
                                f"{student_name} ({student_class}-{student_section})",
                                value=is_selected,
                                key=f"student_{student_id}"
                            ):
                                if student_id not in st.session_state.selected_students:
                                    st.session_state.selected_students.append(student_id)
                            else:
                                if student_id in st.session_state.selected_students:
                                    st.session_state.selected_students.remove(student_id)
                
                # Show selected count
                if st.session_state.selected_students:
                    st.warning(f"⚠️ {len(st.session_state.selected_students)} student(s) selected for deletion")
                    
                    col_clear, col_refresh = st.columns(2)
                    with col_clear:
                        if st.button("🗑️ Clear Selection", type="secondary"):
                            st.session_state.selected_students = []
                            st.rerun()
                    
                    with col_refresh:
                        if st.button("🔄 Refresh List", type="secondary"):
                            st.rerun()
                    
                    st.markdown("---")
                    confirm_delete = st.checkbox(
                        f"Confirm permanent deletion of {len(st.session_state.selected_students)} selected student(s)", 
                        key="confirm_delete_selected_active"
                    )
                    
                    if st.button(
                        f"🚨 Permanently Delete ({len(st.session_state.selected_students)}) Students", 
                        type="primary" if confirm_delete else "secondary", 
                        disabled=not confirm_delete
                    ):
                        with st.spinner("Deleting selected students..."):
                            try:
                                success_count = 0
                                failed_count = 0
                                for student_id in list(st.session_state.selected_students):
                                    try:
                                        if Student.delete_student(int(student_id)):
                                            success_count += 1
                                        else:
                                            failed_count += 1
                                    except Exception as student_error:
                                        failed_count += 1
                                
                                st.session_state.selected_students = []
                                if success_count > 0:
                                    st.success(f"✅ Successfully deleted {success_count} student(s)!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete any students")
                            except Exception as e:
                                st.error(f"❌ Error during deletion: {str(e)}")
                else:
                    st.info("No students selected for deletion")
                    
            else:
                st.info("📊 No students found in database")
                
        except Exception as e:
            st.error(f"❌ Error loading students: {str(e)}")
    
    with col2:
        st.markdown("#### Reset to Sample Data")
        st.info("Clear all existing student and academic records, and populate fresh sample cohort with subjects, marks, and attendance.")
        
        confirm_reset = st.checkbox("Confirm database reset with fresh sample data", key="confirm_reset_sample_active")
        if st.button("🔄 Reset to Sample Data", type="primary" if confirm_reset else "secondary", disabled=not confirm_reset):
            with st.spinner("Resetting to sample data..."):
                try:
                    if reset_to_sample_data():
                        st.success("✅ Reset to sample data successful!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to reset to sample data")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown("---")

    # Data Summary
    st.markdown("### 📊 Data Summary")
    
    try:
        data_summary = get_data_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", data_summary['total_students'])
        
        with col2:
            st.metric("Total Subjects", data_summary['total_subjects'])
        
        with col3:
            st.metric("Total Assessments", data_summary['total_assessments'])
        
        with col4:
            st.metric("Average Performance", f"{data_summary['average_percentage']}%")
        
        # Grade distribution
        if data_summary['grade_distribution']:
            st.markdown("#### Grade Distribution")
            grade_cols = st.columns(len(data_summary['grade_distribution']))
            
            for i, (grade, count) in enumerate(data_summary['grade_distribution'].items()):
                with grade_cols[i]:
                    st.metric(grade, count)
        
        # Sample data indicator
        if data_summary['is_sample_data']:
            st.success("✅ Sample data detected in database")
        elif data_summary['total_students'] > 0:
            st.info("📝 Custom data detected in database")
        else:
            st.warning("⚠️ No data found in database")
            
    except Exception as e:
        st.error(f"Error loading data summary: {str(e)}")

    st.markdown("---")

    with st.expander("⚠️ Danger Zone - Data Deletion & Factory Reset"):
        st.error("**WARNING**: These operations permanently remove database records and cannot be undone!")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("##### 🗑️ Clear Marks")
            confirm_m = st.checkbox("Confirm wipe marks", key="chk_clear_marks_active")
            if st.button("Clear Marks", disabled=not confirm_m, use_container_width=True):
                try:
                    execute_query("DELETE FROM Marks")
                    st.success("✅ All marks cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        with col2:
            st.markdown("##### 👥 Clear Students")
            confirm_s = st.checkbox("Confirm wipe students", key="chk_clear_students_active")
            if st.button("Clear Students", disabled=not confirm_s, use_container_width=True):
                try:
                    execute_query("DELETE FROM Attendance")
                    execute_query("DELETE FROM Marks")
                    execute_query("DELETE FROM Student")
                    st.success("✅ All students and records cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        with col3:
            st.markdown("##### 📚 Clear Subjects")
            confirm_sub = st.checkbox("Confirm wipe subjects", key="chk_clear_subjects_active")
            if st.button("Clear Subjects", disabled=not confirm_sub, use_container_width=True):
                try:
                    execute_query("DELETE FROM Marks")
                    execute_query("DELETE FROM Subject")
                    st.success("✅ All subjects cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        with col4:
            st.markdown("##### 🚨 Wipe Everything")
            confirm_all = st.checkbox("Confirm factory reset", key="chk_clear_all_active")
            if st.button("Factory Reset", type="primary", disabled=not confirm_all, use_container_width=True):
                try:
                    delete_all_data()
                    st.success("✅ Complete database wiped clean")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

elif settings_category == "Data Import/Export":
    st.subheader("📤📥 Data Import/Export")

    # Export section
    st.markdown("### 📤 Export Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Export Students")
        try:
            students = Student.get_all_students()
            if students:
                df = pd.DataFrame(students, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Students CSV",
                    data=csv,
                    file_name=f"students_export_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No students to export")
        except Exception as e:
            st.error(f"Export error: {str(e)}")

    with col2:
        st.markdown("#### Export Subjects")
        try:
            subjects = Subject.get_all_subjects()
            if subjects:
                df = pd.DataFrame(subjects, columns=['ID', 'Subject Name', 'Created'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Subjects CSV",
                    data=csv,
                    file_name=f"subjects_export_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No subjects to export")
        except Exception as e:
            st.error(f"Export error: {str(e)}")

    with col3:
        st.markdown("#### Export Marks")
        try:
            marks = Marks.get_all_marks()
            if marks:
                df = pd.DataFrame(marks, columns=[
                    'Mark ID', 'Student', 'Subject', 'Marks Obtained', 
                    'Max Marks', 'Assessment Date', 'Assessment Type', 
                    'Created', 'Student ID', 'Subject ID'
                ])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Marks CSV",
                    data=csv,
                    file_name=f"marks_export_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No marks to export")
        except Exception as e:
            st.error(f"Export error: {str(e)}")

    st.markdown("---")

    # Import section
    st.markdown("### 📥 Import Data")

    st.info("📋 Import data from CSV files. Ensure your files match the expected format.")

    tab1, tab2, tab3 = st.tabs(["Import Students", "Import Subjects", "Import Marks"])

    with tab1:
        st.markdown("#### Import Students from CSV")
        st.markdown("**Expected format:** Name, Class, Section, DOB (YYYY-MM-DD)")

        uploaded_students = st.file_uploader(
            "Choose students CSV file",
            type=['csv'],
            key="students_upload"
        )

        if uploaded_students:
            try:
                df = pd.read_csv(uploaded_students)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Students"):
                    st.info("Import functionality coming soon!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with tab2:
        st.markdown("#### Import Subjects from CSV")
        st.markdown("**Expected format:** Subject Name")

        uploaded_subjects = st.file_uploader(
            "Choose subjects CSV file",
            type=['csv'],
            key="subjects_upload"
        )

        if uploaded_subjects:
            try:
                df = pd.read_csv(uploaded_subjects)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Subjects"):
                    st.info("Import functionality coming soon!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with tab3:
        st.markdown("#### Import Marks from CSV")
        st.markdown("**Expected format:** Student ID, Subject ID, Marks Obtained, Max Marks, Assessment Date, Assessment Type")

        uploaded_marks = st.file_uploader(
            "Choose marks CSV file",
            type=['csv'],
            key="marks_upload"
        )

        if uploaded_marks:
            try:
                df = pd.read_csv(uploaded_marks)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Marks"):
                    st.info("Import functionality coming soon!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

elif settings_category == "System Information":
    st.subheader("ℹ️ System Information")

    # Application information
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📱 Application Info")

        app_info = {
            "Application": "Student Performance Tracker",
            "Version": "2.0.0 (SQLite)",
            "Framework": "Streamlit",
            "Database": "SQLite",
            "Python Version": "3.x",
            "Last Updated": "2024"
        }

        for key, value in app_info.items():
            st.write(f"**{key}:** {value}")

    with col2:
        st.markdown("### 📊 Database Statistics")

        try:
            db_info = get_database_info()

            db_stats = {
                "Total Students": db_info.get('student_count', 0),
                "Total Subjects": db_info.get('subject_count', 0),
                "Total Assessments": db_info.get('marks_count', 0),
                "Database Size": f"{db_info.get('database_size', 0) / 1024:.1f} KB",
                "Database Exists": "Yes" if db_info.get('database_exists', False) else "No"
            }

            for key, value in db_stats.items():
                st.write(f"**{key}:** {value}")

        except Exception as e:
            st.error(f"Could not load database statistics: {str(e)}")

    st.markdown("---")

    # System requirements
    st.markdown("### 💻 System Requirements")

    requirements = {
        "Python": "3.8 or higher",
        "RAM": "512MB minimum, 1GB recommended",
        "Storage": "100MB for application, additional for data",
        "Database": "SQLite 3.x (built-in)",
        "Browser": "Modern web browser (Chrome, Firefox, Safari, Edge)"
    }

    for requirement, details in requirements.items():
        st.write(f"**{requirement}:** {details}")

    st.markdown("---")

    # Feature list
    st.markdown("### ✨ Features")

    features = [
        "✅ Student Management (CRUD operations)",
        "✅ Subject Management with quick add",
        "✅ Marks Entry with validation and grading",
        "✅ Individual Student Report Cards",
        "✅ Class Performance Analytics",
        "✅ Interactive Visual Reports",
        "✅ CSV Export capabilities",
        "✅ Search and Filter functionality",
        "✅ SQLite Database Management",
        "✅ Responsive design",
        "✅ Sample Data Generation",
        "🔄 Data Import (Coming Soon)",
        "🔄 Advanced Analytics (Coming Soon)",
        "🔄 PDF Export (Coming Soon)"
    ]

    for feature in features:
        st.write(feature)

elif settings_category == "Application Preferences":
    st.subheader("🎛️ Application Preferences")

    st.info("👤 Preferences are stored in browser session and will reset when you close the app")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎨 Display Settings")

        # Theme selection
        current_theme_val = get_current_theme()
        theme_sel = st.selectbox(
            "Application Theme",
            options=["🌙 Dark Mode", "☀️ Light Mode"],
            index=0 if current_theme_val == "dark" else 1,
            help="Select application color scheme (Light or Dark)"
        )
        selected_theme = "dark" if "Dark" in theme_sel else "light"
        if selected_theme != current_theme_val:
            st.session_state.app_theme = selected_theme
            st.rerun()

        # Page size preferences
        default_page_size = st.selectbox(
            "Default Page Size",
            options=[10, 25, 50, 100],
            index=0,
            help="Default number of items per page in tables"
        )

        # Auto-refresh
        auto_refresh = st.checkbox(
            "Auto-refresh data",
            help="Automatically refresh data every 30 seconds"
        )

        # Compact view
        compact_view = st.checkbox(
            "Compact table view",
            help="Use smaller fonts and spacing in tables"
        )

    with col2:
        st.markdown("### 📊 Default Settings")

        # Default class/section for new entries
        default_class = st.selectbox(
            "Default Class",
            options=["", "10", "11", "12"],
            help="Default class for new student entries"
        )

        default_section = st.selectbox(
            "Default Section", 
            options=["", "A", "B", "C"],
            help="Default section for new student entries"
        )

        # Default assessment type
        default_assessment = st.selectbox(
            "Default Assessment Type",
            options=["Assignment", "Quiz", "Midterm", "Final"],
            help="Default type for new marks entries"
        )

        # Grade threshold
        pass_threshold = st.slider(
            "Pass Threshold (%)",
            min_value=30,
            max_value=50,
            value=40,
            help="Percentage required to pass"
        )

    # Save preferences
    if st.button("💾 Save Preferences"):
        # Store in session state
        st.session_state.update({
            'theme': theme,
            'default_page_size': default_page_size,
            'auto_refresh': auto_refresh,
            'compact_view': compact_view,
            'default_class': default_class,
            'default_section': default_section,
            'default_assessment': default_assessment,
            'pass_threshold': pass_threshold
        })
        st.success("✅ Preferences saved for this session!")

    st.markdown("---")

    # Reset preferences
    if st.button("🔄 Reset to Defaults"):
        # Clear relevant session state
        keys_to_clear = [
            'theme', 'default_page_size', 'auto_refresh', 'compact_view',
            'default_class', 'default_section', 'default_assessment', 'pass_threshold'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Preferences reset to defaults!")
        st.rerun()

elif settings_category == "Backup & Restore":
    st.subheader("💾 Backup & Restore")

    st.warning("⚠️ Regular backups are recommended to prevent data loss")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Create Backup")

        st.info("Create a complete backup of all system data")

        backup_format = st.radio(
            "Backup Format:",
            options=["Database Copy (.db)", "CSV Archive (.zip)"],
            help="Choose the format for your backup"
        )

        try:
            db_conn = get_db_connection()
            if backup_format == "Database Copy (.db)":
                st.caption("Creates an atomic, production-safe snapshot of the active SQLite database.")
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                    tmp_path = tmp.name
                try:
                    src_conn = sqlite3.connect(str(db_conn.db_path))
                    dst_conn = sqlite3.connect(tmp_path)
                    src_conn.backup(dst_conn)
                    dst_conn.close()
                    src_conn.close()
                    with open(tmp_path, "rb") as f:
                        db_bytes = f.read()
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

                st.download_button(
                    label="📥 Download Database Backup (.db)",
                    data=db_bytes,
                    file_name=f"student_tracker_backup_{date.today().strftime('%Y%m%d')}.db",
                    mime="application/x-sqlite3",
                    type="primary",
                    use_container_width=True
                )

            else:  # CSV Archive (.zip)
                students = Student.get_all_students()
                subjects = Subject.get_all_subjects()
                marks = Marks.get_all_marks()

                import zipfile
                import io

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    if students:
                        students_df = pd.DataFrame(students, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
                        zip_file.writestr("students.csv", students_df.to_csv(index=False))
                    if subjects:
                        subjects_df = pd.DataFrame(subjects, columns=['ID', 'Subject Name', 'Created'])
                        zip_file.writestr("subjects.csv", subjects_df.to_csv(index=False))
                    if marks:
                        marks_df = pd.DataFrame(marks, columns=[
                            'Mark ID', 'Student', 'Subject', 'Marks Obtained', 
                            'Max Marks', 'Assessment Date', 'Assessment Type', 
                            'Created', 'Student ID', 'Subject ID'
                        ])
                        zip_file.writestr("marks.csv", marks_df.to_csv(index=False))

                zip_buffer.seek(0)
                st.download_button(
                    label="📥 Download CSV Backup Archive (.zip)",
                    data=zip_buffer.read(),
                    file_name=f"student_tracker_csv_{date.today().strftime('%Y%m%d')}.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Backup preparation failed: {str(e)}")

    with col2:
        st.markdown("### 📥 Restore from Backup")
        st.info("Restore system data from a previous database (.db) or ZIP backup file")

        uploaded_backup = st.file_uploader(
            "Choose backup file",
            type=['db', 'zip'],
            help="Select your .db or .zip backup file"
        )

        if uploaded_backup:
            st.success(f"File '{uploaded_backup.name}' loaded ({uploaded_backup.size} bytes)")

            overwrite_existing = st.checkbox(
                "I confirm I want to overwrite existing database data",
                help="⚠️ This will replace current system data with the backup contents"
            )

            if st.button("🔄 Execute Restore", type="primary", use_container_width=True, disabled=not overwrite_existing):
                with st.spinner("Restoring system database..."):
                    try:
                        db_conn = get_db_connection()
                        file_bytes = uploaded_backup.getvalue()

                        if uploaded_backup.name.endswith('.db'):
                            # Validate SQLite header
                            if not file_bytes.startswith(b"SQLite format 3\000"):
                                st.error("❌ Invalid SQLite file format.")
                            else:
                                # Safe swap
                                target_path = db_conn.db_path
                                db_conn.disconnect()
                                backup_path = target_path.with_name("student_tracker_pre_restore.db")
                                if target_path.exists():
                                    import shutil
                                    shutil.copy2(target_path, backup_path)

                                with open(target_path, "wb") as f:
                                    f.write(file_bytes)

                                # Reconnect and verify
                                init_database(populate_sample=False)
                                st.success("✅ Database restored successfully from SQLite backup!")
                                st.balloons()
                                st.rerun()

                        elif uploaded_backup.name.endswith('.zip'):
                            import zipfile
                            import io
                            from utils.data_management import delete_all_data

                            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
                                namelist = z.namelist()
                                delete_all_data()

                                if "students.csv" in namelist:
                                    st_df = pd.read_csv(z.open("students.csv"))
                                    for _, row in st_df.iterrows():
                                        Student.add_student(str(row['Name']), str(row['Class']), str(row['Section']), row.get('DOB'))

                                if "subjects.csv" in namelist:
                                    sb_df = pd.read_csv(z.open("subjects.csv"))
                                    for _, row in sb_df.iterrows():
                                        Subject.add_subject(str(row['Subject Name']))

                                if "marks.csv" in namelist:
                                    mk_df = pd.read_csv(z.open("marks.csv"))
                                    for _, row in mk_df.iterrows():
                                        Marks.add_marks(
                                            int(row['Student ID']), int(row['Subject ID']),
                                            int(row['Marks Obtained']), int(row.get('Max Marks', 100)),
                                            row.get('Assessment Date'), str(row.get('Assessment Type', 'Assignment'))
                                        )

                            st.success("✅ Data successfully restored from CSV archive!")
                            st.balloons()
                            st.rerun()

                    except Exception as rest_err:
                        st.error(f"❌ Restore failed: {str(rest_err)}")

# Footer with support information
st.markdown("---")
st.markdown("### 📞 Support & Help")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📧 Email Support**")
    st.write("gouransh1024@gmail.com")

with col2:
    st.markdown("**📖 Documentation**")  
    st.write("Available in Help sections")

with col3:
    st.markdown("**🐛 Report Issues**")
    st.write("Use the help sections in each page")

# Quick actions sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🚀 Quick Actions")

    if st.button("🏠 Go to Dashboard", use_container_width=True):
        st.switch_page("app.py")

    if st.button("👥 Manage Students", use_container_width=True):
        st.switch_page("pages/1_Manage_Students.py")

    if st.button("📝 Enter Marks", use_container_width=True):
        st.switch_page("pages/3_Enter_Update_Marks.py")

    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/5_Class_Analytics.py")
