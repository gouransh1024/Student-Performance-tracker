"""
Student Model - CRUD operations for Student entity (SQLite version)
Enhanced with Roll Number, Email, and advanced search
"""
import re
import streamlit as st
import pandas as pd
from datetime import datetime, date
from db.connection import execute_query, fetch_all, fetch_one

class Student:
    def __init__(self, student_id=None, name=None, class_name=None, section=None, dob=None, roll_no="", email=""):
        self.student_id = student_id
        self.name = name
        self.class_name = class_name
        self.section = section
        self.dob = dob
        self.roll_no = roll_no
        self.email = email

    @staticmethod
    def add_student(name: str, class_name: str, section: str, dob: date, roll_no: str = "", email: str = "") -> bool:
        """Add new student to database"""
        roll_no = roll_no.strip() if roll_no else ""
        email = email.strip() if email else ""
        query = "INSERT INTO Student (name, class, section, dob, roll_no, email) VALUES (?, ?, ?, ?, ?, ?)"
        return execute_query(query, (name.strip(), class_name.strip(), section.strip(), dob, roll_no, email))

    @staticmethod
    def get_all_students() -> list:
        """Get all students from database with roll_no and email"""
        query = """
        SELECT student_id, name, class, section, dob, 
               COALESCE(roll_no, '') as roll_no, 
               COALESCE(email, '') as email, 
               created_at 
        FROM Student 
        ORDER BY class, section, name
        """
        return fetch_all(query)

    @staticmethod
    def get_student_by_id(student_id: int) -> tuple:
        """Get student by ID including roll_no and email"""
        query = """
        SELECT student_id, name, class, section, dob, 
               COALESCE(roll_no, '') as roll_no, 
               COALESCE(email, '') as email 
        FROM Student 
        WHERE student_id = ?
        """
        return fetch_one(query, (student_id,))

    @staticmethod
    def get_student_by_roll_no(identifier: str) -> tuple:
        """Search student by exact roll number or student ID"""
        clean_id = str(identifier).strip()
        query = """
        SELECT student_id, name, class, section, dob, 
               COALESCE(roll_no, '') as roll_no, 
               COALESCE(email, '') as email 
        FROM Student 
        WHERE LOWER(roll_no) = LOWER(?) OR student_id = ?
        LIMIT 1
        """
        int_id = int(clean_id) if clean_id.isdigit() else -1
        return fetch_one(query, (clean_id, int_id))

    @staticmethod
    def search_students(search_term: str = "", class_filter: str = "", section_filter: str = "") -> list:
        """Search students with flexible filters across name, roll_no, class, section"""
        query = """
        SELECT student_id, name, class, section, dob, 
               COALESCE(roll_no, '') as roll_no, 
               COALESCE(email, '') as email, 
               created_at 
        FROM Student 
        WHERE (name LIKE ? OR roll_no LIKE ? OR email LIKE ? OR ? = '')
        AND (class = ? OR ? = '')
        AND (section = ? OR ? = '')
        ORDER BY class, section, name
        """
        search_pattern = f"%{search_term.strip()}%"
        return fetch_all(query, (search_pattern, search_pattern, search_pattern, search_term.strip(),
                                 class_filter, class_filter, section_filter, section_filter))

    @staticmethod
    def update_student(student_id: int, name: str, class_name: str, section: str, dob: date, roll_no: str = "", email: str = "") -> bool:
        """Update existing student"""
        roll_no = roll_no.strip() if roll_no else ""
        email = email.strip() if email else ""
        query = """
        UPDATE Student 
        SET name = ?, class = ?, section = ?, dob = ?, roll_no = ?, email = ?
        WHERE student_id = ?
        """
        return execute_query(query, (name.strip(), class_name.strip(), section.strip(), dob, roll_no, email, student_id))

    @staticmethod
    def delete_student(student_id: int) -> bool:
        """Delete student and all associated marks and attendance records"""
        execute_query("DELETE FROM Attendance WHERE student_id = ?", (student_id,))
        execute_query("DELETE FROM Marks WHERE student_id = ?", (student_id,))
        return execute_query("DELETE FROM Student WHERE student_id = ?", (student_id,))

    @staticmethod
    def get_students_by_class(class_name: str, section: str = None) -> list:
        """Get students by class and optionally by section"""
        if section:
            query = """
            SELECT student_id, name, class, section, 
                   COALESCE(roll_no, '') as roll_no, 
                   COALESCE(email, '') as email 
            FROM Student 
            WHERE class = ? AND section = ?
            ORDER BY name
            """
            return fetch_all(query, (class_name, section))
        else:
            query = """
            SELECT student_id, name, class, section, 
                   COALESCE(roll_no, '') as roll_no, 
                   COALESCE(email, '') as email 
            FROM Student 
            WHERE class = ?
            ORDER BY section, name
            """
            return fetch_all(query, (class_name,))

    @staticmethod
    def get_unique_classes() -> list:
        """Get list of unique classes"""
        query = "SELECT DISTINCT class FROM Student ORDER BY class"
        result = fetch_all(query)
        return [row[0] for row in result] if result else []

    @staticmethod
    def get_unique_sections() -> list:
        """Get list of unique sections"""
        query = "SELECT DISTINCT section FROM Student ORDER BY section"
        result = fetch_all(query)
        return [row[0] for row in result] if result else []

    @staticmethod
    def get_students_dataframe() -> pd.DataFrame:
        """Get students as pandas DataFrame"""
        students = Student.get_all_students()
        if students:
            df = pd.DataFrame(students, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Roll No', 'Email', 'Created'])
            df['DOB'] = pd.to_datetime(df['DOB']).dt.date
            df['Created'] = pd.to_datetime(df['Created']).dt.date
            return df
        return pd.DataFrame()

    @staticmethod
    def validate_student_data(name: str, class_name: str, section: str, dob: date, roll_no: str = "", email: str = "") -> tuple:
        """Validate student data before insertion/update"""
        errors = []

        # Name validation
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        elif len(name) > 100:
            errors.append("Name cannot exceed 100 characters")

        # Class validation
        if not class_name or not class_name.strip():
            errors.append("Class is required")
        elif len(class_name) > 20:
            errors.append("Class name cannot exceed 20 characters")

        # Section validation
        if not section or not section.strip():
            errors.append("Section is required")
        elif len(section) > 10:
            errors.append("Section cannot exceed 10 characters")

        # DOB validation
        if not dob:
            errors.append("Date of birth is required")
        elif dob >= date.today():
            errors.append("Date of birth must be in the past")
        elif dob < date(1900, 1, 1):
            errors.append("Invalid date of birth")

        # Email validation (optional)
        if email and email.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email.strip()):
                errors.append("Please provide a valid email address")

        return len(errors) == 0, errors

    @staticmethod
    def auto_assign_missing_roll_numbers():
        """Helper to ensure every student has a clean roll number if empty"""
        students = fetch_all("SELECT student_id, class, section, roll_no FROM Student")
        if not students:
            return
        
        class_counters = {}
        for row in students:
            sid, cls, sec, roll = row[0], str(row[1]), str(row[2]), str(row[3] or '').strip()
            key = f"{cls}-{sec}"
            class_counters[key] = class_counters.get(key, 0) + 1
            if not roll:
                assigned_roll = f"{cls}{sec}-{class_counters[key]:02d}"
                execute_query("UPDATE Student SET roll_no = ? WHERE student_id = ?", (assigned_roll, sid))
