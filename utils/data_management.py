"""
Data Management Utilities - Helper functions for managing application data
"""
import streamlit as st
from db.connection import execute_query, fetch_one, fetch_all
from models.student import Student
from models.subject import Subject
from models.marks import Marks

def is_sample_data_present():
    """
    Check if sample data exists in the database
    Returns: bool - True if sample data exists, False otherwise
    """
    try:
        # Check for sample students (the sample data has 10 specific students)
        sample_student_names = [
            "Aarav Sharma", "Priya Patel", "Rohit Kumar", "Sneha Singh", 
            "Vikram Rao", "Anita Desai", "Kiran Reddy", "Meera Joshi", 
            "Arjun Nair", "Deepika Gupta"
        ]
        
        # Check if any of these sample names exist
        for name in sample_student_names:
            result = fetch_one("SELECT COUNT(*) FROM Student WHERE name = ?", (name,))
            if result and result[0] > 0:
                return True
        
        return False
    except Exception as e:
        st.error(f"Error checking sample data: {str(e)}")
        return False

def get_sample_data_info():
    """
    Get information about sample data in the database
    Returns: dict with sample data statistics
    """
    try:
        students = Student.get_all_students()
        subjects = Subject.get_all_subjects()
        marks = Marks.get_all_marks()
        
        return {
            'student_count': len(students) if students else 0,
            'subject_count': len(subjects) if subjects else 0,
            'marks_count': len(marks) if marks else 0,
            'is_sample_data': is_sample_data_present()
        }
    except Exception as e:
        st.error(f"Error getting sample data info: {str(e)}")
        return {
            'student_count': 0,
            'subject_count': 0,
            'marks_count': 0,
            'is_sample_data': False
        }

SAMPLE_STUDENT_NAMES = [
    "Aarav Sharma", "Priya Patel", "Rohit Kumar", "Sneha Singh", 
    "Vikram Rao", "Anita Desai", "Kiran Reddy", "Meera Joshi", 
    "Arjun Nair", "Deepika Gupta"
]

def delete_sample_data() -> bool:
    """
    Delete ONLY sample data from the database, preserving user-created records.
    Returns: bool - True if successful, False otherwise
    """
    try:
        placeholders = ", ".join(["?"] * len(SAMPLE_STUDENT_NAMES))
        sample_ids = fetch_all(
            f"SELECT student_id FROM Student WHERE name IN ({placeholders})",
            tuple(SAMPLE_STUDENT_NAMES)
        )
        if sample_ids:
            id_list = [row[0] for row in sample_ids]
            id_placeholders = ", ".join(["?"] * len(id_list))
            # Delete attendance and marks belonging to sample students
            execute_query(f"DELETE FROM Attendance WHERE student_id IN ({id_placeholders})", tuple(id_list))
            execute_query(f"DELETE FROM Marks WHERE student_id IN ({id_placeholders})", tuple(id_list))
            # Delete sample students
            execute_query(f"DELETE FROM Student WHERE student_id IN ({id_placeholders})", tuple(id_list))

        # If no students remain, remove unused sample subjects
        remaining_students = fetch_one("SELECT COUNT(*) FROM Student")
        if remaining_students and remaining_students[0] == 0:
            execute_query("DELETE FROM Subject")

        return True
    except Exception as e:
        st.error(f"Error deleting sample data: {str(e)}")
        return False

def delete_all_data() -> bool:
    """
    Explicitly delete ALL data (students, subjects, marks, attendance) from the database
    Returns: bool - True if successful, False otherwise
    """
    try:
        execute_query("DELETE FROM Attendance")
        execute_query("DELETE FROM Marks")
        execute_query("DELETE FROM Student")
        execute_query("DELETE FROM Subject")
        try:
            execute_query("DELETE FROM sqlite_sequence WHERE name IN ('Student', 'Subject', 'Marks', 'Attendance')")
        except Exception:
            pass
        return True
    except Exception as e:
        st.error(f"Error deleting all data: {str(e)}")
        return False

def reset_to_sample_data():
    """
    Clear existing data and restore fresh sample data
    Returns: bool - True if successful, False otherwise
    """
    try:
        from db.connection import initialize_sample_data
        
        # Clear existing data completely
        execute_query("DELETE FROM Attendance")
        execute_query("DELETE FROM Marks")
        execute_query("DELETE FROM Student")
        execute_query("DELETE FROM Subject")
        try:
            execute_query("DELETE FROM sqlite_sequence WHERE name IN ('Student', 'Subject', 'Marks', 'Attendance')")
        except Exception:
            pass
        
        # Reinitialize with fresh sample data
        return initialize_sample_data()
    except Exception as e:
        st.error(f"Error resetting to sample data: {str(e)}")
        return False

def get_data_summary():
    """
    Get a comprehensive summary of all data in the database
    Returns: dict with data summary
    """
    try:
        students = Student.get_all_students()
        subjects = Subject.get_all_subjects()
        marks = Marks.get_all_marks()
        
        # Calculate additional statistics
        if marks:
            total_marks = sum(mark[3] for mark in marks)
            max_possible = sum(mark[4] for mark in marks)
            average_percentage = (total_marks / max_possible * 100) if max_possible > 0 else 0
            
            # Grade distribution
            grade_counts = {}
            for mark in marks:
                percentage = Marks.calculate_percentage(mark[3], mark[4])
                grade = Marks.calculate_grade(percentage)
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        else:
            average_percentage = 0
            grade_counts = {}
        
        return {
            'total_students': len(students) if students else 0,
            'total_subjects': len(subjects) if subjects else 0,
            'total_assessments': len(marks) if marks else 0,
            'average_percentage': round(average_percentage, 2),
            'grade_distribution': grade_counts,
            'is_sample_data': is_sample_data_present()
        }
    except Exception as e:
        st.error(f"Error getting data summary: {str(e)}")
        return {
            'total_students': 0,
            'total_subjects': 0,
            'total_assessments': 0,
            'average_percentage': 0,
            'grade_distribution': {},
            'is_sample_data': False
        }
