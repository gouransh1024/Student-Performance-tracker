"""
SQLite Database Connection Module
Handles database connection, thread-safety, migrations, and initialization for SQLite
"""

import sqlite3
import os
import random
import threading
from typing import Optional, Any
from pathlib import Path
from datetime import date, timedelta

# Thread-local storage for safe connection pooling per thread
_thread_local = threading.local()

def _safe_log_error(msg: str):
    """Log error message to Streamlit UI if available, else print"""
    try:
        import streamlit as st
        st.error(msg)
    except Exception:
        print(f"[DB ERROR] {msg}")

class DatabaseManager:
    """Database connection manager for SQLite with thread-safety and WAL optimizations"""

    def __init__(self, db_path: Optional[str] = None):
        self._custom_db_path = db_path

    @property
    def db_path(self) -> Path:
        if self._custom_db_path:
            return Path(self._custom_db_path)
        env_path = os.environ.get("STUDENT_TRACKER_DB")
        if env_path:
            return Path(env_path)
        return Path(__file__).parent.parent / "student_tracker.db"

    @property
    def connection(self) -> Optional[sqlite3.Connection]:
        """Get thread-local SQLite connection"""
        conn = getattr(_thread_local, "conn", None)
        if conn is None:
            conn = self.get_connection()
            _thread_local.conn = conn
        return conn

    @connection.setter
    def connection(self, val: Optional[sqlite3.Connection]):
        _thread_local.conn = val

    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection with performance and integrity pragmas"""
        try:
            db_target = str(self.db_path)
            conn = sqlite3.connect(
                db_target,
                check_same_thread=False,
                timeout=30.0
            )
            conn.execute("PRAGMA foreign_keys = ON")
            if db_target != ":memory:":
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 1000")
            conn.execute("PRAGMA temp_store = MEMORY")
            return conn
        except Exception as e:
            _safe_log_error(f"Database connection failed: {e}")
            return None

    def connect(self) -> bool:
        """Establish database connection"""
        self.connection = self.get_connection()
        return self.connection is not None

    def disconnect(self):
        """Close current thread's database connection"""
        conn = getattr(_thread_local, "conn", None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            _thread_local.conn = None

    def checkpoint_wal(self):
        """Execute WAL checkpoint to truncate wal log file"""
        try:
            conn = self.connection
            if conn and str(self.db_path) != ":memory:":
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception as e:
            print(f"WAL checkpoint error: {e}")

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT, UPDATE, DELETE queries safely with commit"""
        try:
            conn = self.connection
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            _safe_log_error(f"Query execution failed: {e}")
            return False

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all results from SELECT query"""
        try:
            conn = self.connection
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            _safe_log_error(f"Query fetch failed: {e}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """Fetch single result from SELECT query"""
        try:
            conn = self.connection
            if not conn:
                return None
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            _safe_log_error(f"Query fetch failed: {e}")
            return None

# Global manager instance
_global_db_manager = DatabaseManager()

def get_db_connection() -> Optional[DatabaseManager]:
    """Return database manager instance, verifying connection"""
    if _global_db_manager.connect():
        return _global_db_manager
    return None

# Query helper functions
def execute_query(query: str, params: tuple = None) -> bool:
    db = get_db_connection()
    return db.execute_query(query, params) if db else False

def fetch_all(query: str, params: tuple = None) -> list:
    db = get_db_connection()
    return db.fetch_all(query, params) if db else []

def fetch_one(query: str, params: tuple = None) -> Optional[tuple]:
    db = get_db_connection()
    return db.fetch_one(query, params) if db else None

# Initialization & Migration logic
def initialize_sample_data() -> bool:
    try:
        existing_students = fetch_one("SELECT COUNT(*) FROM Student")
        if existing_students and existing_students[0] > 0:
            print("Sample data already exists")
            return True

        print("Inserting sample data...")

        sample_students = [
            ("Aarav Sharma", "10", "A", "2008-05-20", "10A-01", "aarav.sharma@school.edu"),
            ("Priya Patel", "10", "A", "2008-03-15", "10A-02", "priya.patel@school.edu"),
            ("Rohit Kumar", "10", "B", "2008-07-10", "10B-01", "rohit.kumar@school.edu"),
            ("Sneha Singh", "10", "B", "2008-01-25", "10B-02", "sneha.singh@school.edu"),
            ("Vikram Rao", "11", "A", "2007-11-05", "11A-01", "vikram.rao@school.edu"),
            ("Anita Desai", "11", "A", "2007-09-30", "11A-02", "anita.desai@school.edu"),
            ("Kiran Reddy", "11", "B", "2007-12-18", "11B-01", "kiran.reddy@school.edu"),
            ("Meera Joshi", "12", "A", "2006-08-22", "12A-01", "meera.joshi@school.edu"),
            ("Arjun Nair", "12", "A", "2006-04-14", "12A-02", "arjun.nair@school.edu"),
            ("Deepika Gupta", "12", "B", "2006-06-08", "12B-01", "deepika.gupta@school.edu")
        ]

        sample_subjects = [
            ("Mathematics",), ("Physics",), ("Chemistry",),
            ("Biology",), ("English",), ("History",),
            ("Geography",), ("Computer Science",)
        ]

        for student in sample_students:
            execute_query(
                "INSERT INTO Student (name, class, section, dob, roll_no, email) VALUES (?, ?, ?, ?, ?, ?)",
                student
            )

        for subject in sample_subjects:
            execute_query("INSERT OR IGNORE INTO Subject (subject_name) VALUES (?)", subject)

        inserted_students = fetch_all("SELECT student_id FROM Student ORDER BY student_id")
        inserted_student_ids = [row[0] for row in inserted_students] if inserted_students else []

        inserted_subjects = fetch_all("SELECT subject_id FROM Subject ORDER BY subject_id")
        inserted_subject_ids = [row[0] for row in inserted_subjects] if inserted_subjects else []

        # Populate realistic marks across assessment types
        for s_id in inserted_student_ids:
            # Pick 5 subjects per student
            student_subs = inserted_subject_ids[:5] if len(inserted_subject_ids) >= 5 else inserted_subject_ids
            for sub_id in student_subs:
                for a_type, term in [('Quiz', 'Term 1'), ('Midterm', 'Term 1'), ('Assignment', 'Term 1')]:
                    marks_obtained = random.randint(52, 98)
                    assessment_date = date.today() - timedelta(days=random.randint(2, 45))
                    execute_query(
                        """INSERT INTO Marks 
                        (student_id, subject_id, marks_obtained, max_marks, assessment_date, assessment_type, term)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (s_id, sub_id, marks_obtained, 100, assessment_date, a_type, term)
                    )

        # Populate attendance for the past 20 school days
        for s_id in inserted_student_ids:
            for day_offset in range(1, 21):
                att_date = date.today() - timedelta(days=day_offset)
                if att_date.weekday() < 5:  # Monday to Friday
                    att_status = random.choices(['Present', 'Absent', 'Late'], weights=[0.88, 0.07, 0.05])[0]
                    execute_query(
                        "INSERT OR IGNORE INTO Attendance (student_id, attendance_date, status) VALUES (?, ?, ?)",
                        (s_id, att_date, att_status)
                    )

        print("Sample data inserted successfully with attendance and academic records.")
        return True

    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

def _migrate_schema_if_needed(db: DatabaseManager):
    """Safely migrate legacy schema check constraints and add modern fields"""
    try:
        res = db.fetch_one("SELECT sql FROM sqlite_master WHERE type='table' AND name='Student'")
        if res and res[0] and "CHECK(class IN ('10', '11', '12'))" in res[0]:
            print("Migrating Student table schema to flexible class/section constraints...")
            db.execute_query("PRAGMA foreign_keys = OFF")
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS Student_new (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL CHECK(length(trim(name)) >= 2),
                    class TEXT NOT NULL CHECK(length(trim(class)) > 0),
                    section TEXT NOT NULL CHECK(length(trim(section)) > 0),
                    dob DATE,
                    roll_no TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute_query("""
                INSERT INTO Student_new (student_id, name, class, section, dob, created_at)
                SELECT student_id, name, class, section, dob, created_at FROM Student
            """)
            db.execute_query("DROP TABLE Student")
            db.execute_query("ALTER TABLE Student_new RENAME TO Student")
            db.execute_query("PRAGMA foreign_keys = ON")
            print("Student table migration complete.")

        # Add roll_no and email to Student if missing
        st_cols = [col[1] for col in db.fetch_all("PRAGMA table_info(Student)")]
        if "roll_no" not in st_cols:
            db.execute_query("ALTER TABLE Student ADD COLUMN roll_no TEXT DEFAULT ''")
        if "email" not in st_cols:
            db.execute_query("ALTER TABLE Student ADD COLUMN email TEXT DEFAULT ''")

        # Add term to Marks if missing
        mk_cols = [col[1] for col in db.fetch_all("PRAGMA table_info(Marks)")]
        if "term" not in mk_cols:
            db.execute_query("ALTER TABLE Marks ADD COLUMN term TEXT DEFAULT 'Term 1'")

    except Exception as e:
        print(f"Migration error (non-fatal): {e}")

def init_database(populate_sample: bool = True) -> bool:
    db = get_db_connection()
    if not db:
        return False

    try:
        # Ensure foreign keys are enabled
        db.execute_query("PRAGMA foreign_keys = ON")
        
        student_table_sql = """
        CREATE TABLE IF NOT EXISTS Student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL 
                CHECK(length(trim(name)) >= 2),
            class TEXT NOT NULL 
                CHECK(length(trim(class)) > 0),
            section TEXT NOT NULL 
                CHECK(length(trim(section)) > 0),
            dob DATE,
            roll_no TEXT DEFAULT '',
            email TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        subject_table_sql = """
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE COLLATE NOCASE
                CHECK(length(trim(subject_name)) >= 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        marks_table_sql = """
        CREATE TABLE IF NOT EXISTS Marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks_obtained INTEGER NOT NULL
                CHECK(marks_obtained >= 0),
            max_marks INTEGER DEFAULT 100
                CHECK(max_marks > 0),
            assessment_date DATE DEFAULT (date('now')),
            assessment_type TEXT DEFAULT 'Assignment'
                CHECK(assessment_type IN ('Quiz', 'Assignment', 'Midterm', 'Final', 'Project')),
            term TEXT DEFAULT 'Term 1',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
            CHECK(marks_obtained <= max_marks)
        )
        """

        attendance_table_sql = """
        CREATE TABLE IF NOT EXISTS Attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date DATE NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
            UNIQUE(student_id, attendance_date)
        )
        """

        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_student_class_section ON Student(class, section)",
            "CREATE INDEX IF NOT EXISTS idx_student_name ON Student(name)",
            "CREATE INDEX IF NOT EXISTS idx_marks_student_id ON Marks(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_marks_subject_id ON Marks(subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_marks_assessment_date ON Marks(assessment_date)",
            "CREATE INDEX IF NOT EXISTS idx_marks_student_subject ON Marks(student_id, subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON Attendance(student_id, attendance_date)"
        ]

        for table_sql in [student_table_sql, subject_table_sql, marks_table_sql, attendance_table_sql]:
            db.execute_query(table_sql)

        # Run safe migration if existing DB has old schema constraints or missing columns
        _migrate_schema_if_needed(db)

        for index_sql in indexes_sql:
            db.execute_query(index_sql)

        if populate_sample:
            initialize_sample_data()

        # Checkpoint WAL
        db.checkpoint_wal()
        return True

    except Exception as e:
        _safe_log_error(f"Database initialization failed: {e}")
        return False

def get_database_info() -> dict:
    db = get_db_connection()
    if not db:
        return {}

    try:
        info = {
            "database_path": str(db.db_path),
            "database_exists": db.db_path.exists(),
            "database_size": db.db_path.stat().st_size if db.db_path.exists() else 0
        }

        for table in ["Student", "Subject", "Marks"]:
            result = db.fetch_one(f"SELECT COUNT(*) FROM {table}")
            info[f"{table.lower()}_count"] = result[0] if result else 0

        return info

    except Exception as e:
        _safe_log_error(f"Error getting database info: {e}")
        return {}

def debug_database():
    try:
        students = fetch_all("SELECT COUNT(*) FROM Student")
        subjects = fetch_all("SELECT COUNT(*) FROM Subject")
        marks = fetch_all("SELECT COUNT(*) FROM Marks")

        print(f"Students: {students[0][0] if students else 0}")
        print(f"Subjects: {subjects[0][0] if subjects else 0}")
        print(f"Marks: {marks[0][0] if marks else 0}")

        all_students = fetch_all("SELECT * FROM Student LIMIT 5")
        print("Sample students:" if all_students else "No students found", all_students)

    except Exception as e:
        print(f"Debug error: {e}")
