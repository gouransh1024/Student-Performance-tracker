"""
Attendance Model - Management and analytics for student attendance
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
import random
from db.connection import execute_query, fetch_all, fetch_one

class Attendance:
    @staticmethod
    def mark_attendance(student_id: int, attendance_date: date, status: str) -> bool:
        """Mark or update student attendance for a given date"""
        if status not in ('Present', 'Absent', 'Late'):
            return False
        query = """
        INSERT INTO Attendance (student_id, attendance_date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id, attendance_date) DO UPDATE SET status = excluded.status
        """
        return execute_query(query, (student_id, attendance_date, status))

    @staticmethod
    def get_student_attendance_summary(student_id: int) -> dict:
        """Calculate attendance metrics for a student"""
        records = fetch_all(
            "SELECT status FROM Attendance WHERE student_id = ?",
            (student_id,)
        )
        if not records:
            return {
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'late_days': 0,
                'attendance_rate': 100.0
            }

        total = len(records)
        present = sum(1 for r in records if r[0] == 'Present')
        absent = sum(1 for r in records if r[0] == 'Absent')
        late = sum(1 for r in records if r[0] == 'Late')
        # Weighted attendance rate: Present = 1.0, Late = 0.5, Absent = 0.0
        effective_present = present + (0.5 * late)
        rate = round((effective_present / total) * 100, 1) if total > 0 else 100.0

        return {
            'total_days': total,
            'present_days': present,
            'absent_days': absent,
            'late_days': late,
            'attendance_rate': rate
        }

    @staticmethod
    def get_attendance_records(student_id: int, limit: int = 30) -> list:
        """Retrieve recent attendance entries for a student"""
        query = """
        SELECT attendance_id, attendance_date, status
        FROM Attendance
        WHERE student_id = ?
        ORDER BY attendance_date DESC
        LIMIT ?
        """
        return fetch_all(query, (student_id, limit))

    @staticmethod
    def get_class_attendance_summary(class_name: str, section: str = None) -> dict:
        """Calculate aggregated attendance for a class or section"""
        if section and section != "All":
            query = """
            SELECT a.status
            FROM Attendance a
            JOIN Student s ON a.student_id = s.student_id
            WHERE s.class = ? AND s.section = ?
            """
            params = (class_name, section)
        elif class_name and class_name != "All":
            query = """
            SELECT a.status
            FROM Attendance a
            JOIN Student s ON a.student_id = s.student_id
            WHERE s.class = ?
            """
            params = (class_name,)
        else:
            query = "SELECT status FROM Attendance"
            params = ()

        records = fetch_all(query, params)
        if not records:
            return {
                'total_records': 0,
                'overall_attendance_rate': 100.0,
                'present_rate': 100.0,
                'present_count': 0,
                'absent_count': 0,
                'late_count': 0
            }

        total = len(records)
        present = sum(1 for r in records if r[0] == 'Present')
        absent = sum(1 for r in records if r[0] == 'Absent')
        late = sum(1 for r in records if r[0] == 'Late')
        rate = round(((present + 0.5 * late) / total) * 100, 1)

        return {
            'total_records': total,
            'overall_attendance_rate': rate,
            'present_rate': rate,
            'present_count': present,
            'absent_count': absent,
            'late_count': late
        }

    @staticmethod
    def get_all_students_attendance_correlation(class_name: Optional[str] = None, section: Optional[str] = None) -> List[Dict]:
        """Fetch attendance vs academic percentage data for correlation plotting"""
        conditions = []
        params = []
        if class_name and class_name != "All":
            conditions.append("s.class = ?")
            params.append(class_name)
        if section and section != "All":
            conditions.append("s.section = ?")
            params.append(section)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        query = f"""
        SELECT s.student_id, s.name, s.class, s.section,
               AVG((m.marks_obtained * 100.0) / m.max_marks) as avg_score
        FROM Student s
        JOIN Marks m ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.student_id, s.name, s.class, s.section
        """
        student_rows = fetch_all(query, tuple(params) if params else None)
        data = []
        for s in student_rows:
            sid, name, cls, sec, score = s[0], s[1], s[2], s[3], s[4]
            att = Attendance.get_student_attendance_summary(sid)
            rate = att.get('attendance_rate', 100.0)
            avg_score = round(score, 1) if score is not None else 0.0
            data.append({
                'student_id': sid,
                'name': name,
                'student_name': name,
                'class': f"{cls}-{sec}",
                'attendance_rate': rate,
                'attendance_pct': rate,
                'academic_percentage': avg_score,
                'academic_avg': avg_score,
                'status': 'Pass' if avg_score >= 40 else 'Fail'
            })
        return data

    @staticmethod
    def seed_sample_attendance() -> bool:
        """Seed realistic attendance entries for existing students if table is empty"""
        try:
            existing = fetch_one("SELECT COUNT(*) FROM Attendance")
            if existing and existing[0] > 0:
                return True

            students = fetch_all("SELECT student_id FROM Student")
            if not students:
                return False

            for (sid,) in students:
                for offset in range(1, 25):
                    d = date.today() - timedelta(days=offset)
                    if d.weekday() < 5:  # School days only (Mon-Fri)
                        r = random.random()
                        status = 'Present' if r < 0.88 else ('Late' if r < 0.96 else 'Absent')
                        execute_query(
                            "INSERT OR IGNORE INTO Attendance (student_id, attendance_date, status) VALUES (?, ?, ?)",
                            (sid, d, status)
                        )
            return True
        except Exception as e:
            print(f"Attendance seed error: {e}")
            return False
