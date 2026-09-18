"""
Test Cases for Student Performance Tracker
This file contains unit tests and integration scenarios with test database isolation
"""
import unittest
import sys
import os
import tempfile
from datetime import date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db_connection, init_database
from models.student import Student
from models.subject import Subject
from models.marks import Marks

class BaseTestCase(unittest.TestCase):
    """Base class providing isolated SQLite database for testing"""
    temp_dir = None
    test_db_path = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.test_db_path = os.path.join(cls.temp_dir.name, "test_tracker.db")
        os.environ["STUDENT_TRACKER_DB"] = cls.test_db_path
        db = get_db_connection()
        if db:
            db.disconnect()
        init_database(populate_sample=False)

    @classmethod
    def tearDownClass(cls):
        db = get_db_connection()
        if db:
            db.disconnect()
        import gc
        gc.collect()
        os.environ.pop("STUDENT_TRACKER_DB", None)
        if cls.temp_dir:
            try:
                cls.temp_dir.cleanup()
            except Exception:
                pass


class TestStudentModel(BaseTestCase):
    """Test cases for Student model"""

    def test_validate_student_data(self):
        """Test student data validation"""
        # Valid data
        valid, errors = Student.validate_student_data("John Doe", "10", "A", date(2008, 5, 20))
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid name (too short)
        valid, errors = Student.validate_student_data("J", "10", "A", date(2008, 5, 20))
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid date (future)
        valid, errors = Student.validate_student_data("John Doe", "10", "A", date(2030, 5, 20))
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_student_crud(self):
        """Test adding and retrieving a student"""
        success = Student.add_student("Alice Test", "9", "A", date(2009, 3, 15))
        self.assertTrue(success)
        students = Student.get_all_students()
        names = [s[1] for s in students]
        self.assertIn("Alice Test", names)


class TestSubjectModel(BaseTestCase):
    """Test cases for Subject model"""

    def test_validate_subject_data(self):
        """Test subject data validation"""
        # Valid subject name format
        valid, errors = Subject.validate_subject_data("Mathematics", check_duplicate=False)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid subject name (too short)
        valid, errors = Subject.validate_subject_data("M")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid subject name (too long)
        valid, errors = Subject.validate_subject_data("A" * 51)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_duplicate_subject_validation(self):
        """Test detection of duplicate subjects"""
        Subject.add_subject("UniqueBio")
        valid, errors = Subject.validate_subject_data("UniqueBio", check_duplicate=True)
        self.assertFalse(valid)
        self.assertIn("Subject already exists", errors)


class TestMarksModel(BaseTestCase):
    """Test cases for Marks model"""

    def test_calculate_percentage(self):
        """Test percentage calculation"""
        # Normal case
        percentage = Marks.calculate_percentage(78, 100)
        self.assertEqual(percentage, 78.0)

        # Perfect score
        percentage = Marks.calculate_percentage(100, 100)
        self.assertEqual(percentage, 100.0)

        # Zero marks
        percentage = Marks.calculate_percentage(0, 100)
        self.assertEqual(percentage, 0.0)

        # Edge case: zero max marks
        percentage = Marks.calculate_percentage(50, 0)
        self.assertEqual(percentage, 0.0)

    def test_calculate_grade(self):
        """Test grade calculation thresholds"""
        self.assertEqual(Marks.calculate_grade(95), "A+")
        self.assertEqual(Marks.calculate_grade(90), "A+")
        self.assertEqual(Marks.calculate_grade(85), "A")
        self.assertEqual(Marks.calculate_grade(80), "A")
        self.assertEqual(Marks.calculate_grade(75), "B+")
        self.assertEqual(Marks.calculate_grade(70), "B+")
        self.assertEqual(Marks.calculate_grade(65), "B")
        self.assertEqual(Marks.calculate_grade(60), "B")
        self.assertEqual(Marks.calculate_grade(55), "C+")
        self.assertEqual(Marks.calculate_grade(50), "C+")
        self.assertEqual(Marks.calculate_grade(45), "C")
        self.assertEqual(Marks.calculate_grade(40), "C")
        self.assertEqual(Marks.calculate_grade(39.9), "F")
        self.assertEqual(Marks.calculate_grade(0), "F")

    def test_validate_marks_data(self):
        """Test marks data validation"""
        # Valid marks
        valid, errors = Marks.validate_marks_data(78, 100, date.today())
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid marks (negative)
        valid, errors = Marks.validate_marks_data(-10, 100, date.today())
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid marks (exceeds max)
        valid, errors = Marks.validate_marks_data(120, 100, date.today())
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid max marks (zero)
        valid, errors = Marks.validate_marks_data(50, 0, date.today())
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)


class TestIntegrationScenarios(BaseTestCase):
    """Integration test scenarios"""

    def test_complete_student_workflow(self):
        """Test complete student summary calculation logic"""
        student_summary = {
            'student_name': 'John Doe',
            'total_subjects': 5,
            'total_marks_obtained': 400,
            'total_max_marks': 500,
            'overall_percentage': 80.0,
            'overall_grade': 'A',
            'subject_details': [
                {
                    'subject': 'Mathematics',
                    'marks_obtained': 85,
                    'max_marks': 100,
                    'percentage': 85.0,
                    'grade': 'A',
                    'assessment_date': '2024-01-15',
                    'assessment_type': 'Final'
                },
                {
                    'subject': 'Physics',
                    'marks_obtained': 78,
                    'max_marks': 100,
                    'percentage': 78.0,
                    'grade': 'B+',
                    'assessment_date': '2024-01-16',
                    'assessment_type': 'Final'
                }
            ],
            'pass_fail_status': 'Pass'
        }

        expected_percentage = (400 / 500) * 100
        self.assertEqual(student_summary['overall_percentage'], expected_percentage)
        expected_grade = Marks.calculate_grade(80.0)
        self.assertEqual(student_summary['overall_grade'], expected_grade)
        self.assertEqual(student_summary['pass_fail_status'], 'Pass')

    def test_class_analytics_calculations(self):
        """Test class analytics calculations"""
        students_data = [
            {'name': 'Student A', 'percentage': 85.0, 'grade': 'A'},
            {'name': 'Student B', 'percentage': 75.0, 'grade': 'B+'},
            {'name': 'Student C', 'percentage': 65.0, 'grade': 'B'},
            {'name': 'Student D', 'percentage': 55.0, 'grade': 'C+'},
            {'name': 'Student E', 'percentage': 35.0, 'grade': 'F'}
        ]

        total_percentage = sum(student['percentage'] for student in students_data)
        class_average = total_percentage / len(students_data)
        expected_average = 63.0
        self.assertEqual(class_average, expected_average)

        passing_students = sum(1 for student in students_data if student['percentage'] >= 40)
        pass_rate = (passing_students / len(students_data)) * 100
        expected_pass_rate = 80.0
        self.assertEqual(pass_rate, expected_pass_rate)

    def test_grade_distribution(self):
        """Test grade distribution calculations"""
        grades = ['A+', 'A', 'A', 'B+', 'B+', 'B', 'C+', 'C', 'F', 'F']
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        expected_counts = {
            'A+': 1, 'A': 2, 'B+': 2, 'B': 1, 'C+': 1, 'C': 1, 'F': 2
        }
        self.assertEqual(grade_counts, expected_counts)


class TestAcademicIntelligenceEngine(BaseTestCase):
    """Test suite for GPA, CGPA, weighted assessments, and at-risk detection"""

    def test_gpa_calculation(self):
        """Test standard 4.0 scale GPA calculation"""
        self.assertEqual(Marks.calculate_gpa(95.0), 4.0)
        self.assertEqual(Marks.calculate_gpa(85.0), 3.7)
        self.assertEqual(Marks.calculate_gpa(75.0), 3.3)
        self.assertEqual(Marks.calculate_gpa(65.0), 3.0)
        self.assertEqual(Marks.calculate_gpa(55.0), 2.3)
        self.assertEqual(Marks.calculate_gpa(45.0), 2.0)
        self.assertEqual(Marks.calculate_gpa(35.0), 0.0)

    def test_cgpa_calculation(self):
        """Test standard 10.0 scale CGPA calculation"""
        self.assertEqual(Marks.calculate_cgpa(95.0), 10.0)
        self.assertEqual(Marks.calculate_cgpa(85.0), 9.0)
        self.assertEqual(Marks.calculate_cgpa(75.0), 8.0)
        self.assertEqual(Marks.calculate_cgpa(65.0), 7.0)
        self.assertEqual(Marks.calculate_cgpa(55.0), 6.0)
        self.assertEqual(Marks.calculate_cgpa(45.0), 5.0)
        self.assertEqual(Marks.calculate_cgpa(35.0), 0.0)

    def test_weighted_percentage(self):
        """Test calculation of weighted assessment averages"""
        assessments = [
            {'marks_obtained': 80, 'max_marks': 100, 'type': 'Assignment'},  # 15% weight
            {'marks_obtained': 90, 'max_marks': 100, 'type': 'Quiz'},        # 10% weight
            {'marks_obtained': 70, 'max_marks': 100, 'type': 'Midterm'},     # 25% weight
            {'marks_obtained': 85, 'max_marks': 100, 'type': 'Final'}        # 40% weight
        ]
        weighted_pct = Marks.calculate_weighted_percentage(assessments)
        self.assertGreater(weighted_pct, 70.0)
        self.assertLess(weighted_pct, 90.0)

    def test_student_roll_no_and_email(self):
        """Test adding student with roll_no and email, and searching by roll_no"""
        Student.add_student("Rolled Student", "12", "C", date(2006, 1, 1), roll_no="12C-99", email="test@school.edu")
        found = Student.get_student_by_roll_no("12C-99")
        self.assertIsNotNone(found)
        self.assertEqual(found[1], "Rolled Student")
        self.assertEqual(found[5], "12C-99")
        self.assertEqual(found[6], "test@school.edu")


class TestAttendanceModel(BaseTestCase):
    """Test suite for Attendance tracking and correlation"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Student.add_student("Att Student 1", "10", "Z", date(2008, 1, 1))
        cls.student = Student.search_students("Att Student 1")[0]
        cls.student_id = cls.student[0]

    def test_mark_and_retrieve_attendance(self):
        """Test recording daily student attendance"""
        from models.attendance import Attendance
        today = date.today()
        self.assertTrue(Attendance.mark_attendance(self.student_id, today, "Present"))
        
        summary = Attendance.get_student_attendance_summary(self.student_id)
        self.assertEqual(summary['present_days'], 1)
        self.assertEqual(summary['attendance_rate'], 100.0)

    def test_class_attendance_summary(self):
        """Test cohort attendance aggregation"""
        from models.attendance import Attendance
        summary = Attendance.get_class_attendance_summary("10", "Z")
        self.assertIn('overall_attendance_rate', summary)
        self.assertGreaterEqual(summary['overall_attendance_rate'], 0.0)

    def test_attendance_correlation_and_scatter(self):
        """Test attendance correlation data format and scatter chart generation"""
        from models.attendance import Attendance
        from utils.chart_theme import create_attendance_scatter
        corr = Attendance.get_all_students_attendance_correlation("10", "Z")
        self.assertIsInstance(corr, list)
        if corr:
            item = corr[0]
            self.assertIn('attendance_pct', item)
            self.assertIn('attendance_rate', item)
            self.assertIn('academic_avg', item)
            self.assertIn('student_name', item)
            self.assertIn('status', item)
        fig = create_attendance_scatter(corr)
        self.assertIsNotNone(fig)


class TestPdfAndZipExport(BaseTestCase):
    """Test suite for single PDF report card and batch class ZIP generation"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Student.add_student("Report Card Test", "10", "Y", date(2008, 2, 2), roll_no="10Y-01")
        cls.student = Student.search_students("Report Card Test")[0]
        cls.student_id = cls.student[0]
        Subject.add_subject("Science Test")
        sub = Subject.get_subject_by_name("Science Test")
        cls.subject_id = sub[0]
        Marks.add_marks(cls.student_id, cls.subject_id, 88, 100, date.today(), "Exam", "Term 1")

    def test_single_student_pdf_generation(self):
        """Verify report card PDF compiles to valid PDF format"""
        from utils.pdf_generator import generate_student_report_pdf
        from models.attendance import Attendance
        student_info = Student.get_student_by_id(self.student_id)
        student_summary = Marks.get_student_summary(self.student_id)
        att_summary = Attendance.get_student_attendance_summary(self.student_id)

        pdf_bytes = generate_student_report_pdf(student_summary, student_info, att_summary)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1000)

    def test_batch_class_zip_generation(self):
        """Verify batch class report card ZIP compiles cleanly and contains PDFs"""
        import zipfile
        import io
        from utils.pdf_generator import generate_class_report_cards_zip

        zip_bytes = generate_class_report_cards_zip("10", "Y")
        self.assertIsInstance(zip_bytes, bytes)
        self.assertGreater(len(zip_bytes), 500)

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            file_names = zf.namelist()
            self.assertGreater(len(file_names), 0)
            self.assertTrue(file_names[0].endswith(".pdf"))


def run_all_tests():
    """Run all test cases"""
    test_suite = unittest.TestSuite()
    test_classes = [
        TestStudentModel,
        TestSubjectModel, 
        TestMarksModel,
        TestIntegrationScenarios,
        TestAcademicIntelligenceEngine,
        TestAttendanceModel,
        TestPdfAndZipExport
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite)

if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

