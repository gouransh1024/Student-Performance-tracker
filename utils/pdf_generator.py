"""
PDF Report Card Generator Module
Uses ReportLab to generate professional, publication-quality academic report cards
and batch ZIP archives for entire classes.
"""
import io
import re
import zipfile
from datetime import date, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

def generate_student_report_pdf(student_summary: dict, student_info: tuple, attendance_summary: dict = None) -> bytes:
    """
    Generate an academic report card PDF for a student
    
    Args:
        student_summary: Dict containing student performance analytics (from Marks.get_student_summary)
        student_info: Tuple of (student_id, name, class, section, dob, [roll_no], [email])
        attendance_summary: Optional dict containing attendance stats (rate, present_days, total_days)
        
    Returns:
        bytes: Raw PDF content in bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=1,  # Center
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#64748B'),
        alignment=1,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#3B82F6'),
        spaceBefore=10,
        spaceAfter=6
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    bold_cell_style = ParagraphStyle(
        'TableBoldCell',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0F172A')
    )

    # 1. Header Banner
    story.append(Paragraph("ACADEMIC PERFORMANCE & EVALUATION REPORT", title_style))
    story.append(Paragraph(f"Official Institutional Progress Record &bull; Academic Year {date.today().year} - {date.today().year + 1}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4F46E5'), spaceAfter=12))

    # 2. Student Information Table
    student_id = student_info[0] if student_info else "N/A"
    student_name = student_summary.get('student_name', (student_info[1] if student_info else "Unknown"))
    class_sec = f"{student_info[2]}-{student_info[3]}" if student_info and len(student_info) >= 4 else "N/A"
    dob_val = student_info[4] if student_info and len(student_info) > 4 else "N/A"
    if isinstance(dob_val, (date, datetime)):
        dob_str = dob_val.strftime('%B %d, %Y')
    else:
        dob_str = str(dob_val)

    roll_no = student_info[5] if student_info and len(student_info) > 5 and student_info[5] else f"ID-{student_id}"
    email = student_info[6] if student_info and len(student_info) > 6 and student_info[6] else "N/A"

    att_rate_str = "N/A"
    if attendance_summary and attendance_summary.get('total_days', 0) > 0:
        att_rate_str = f"{attendance_summary.get('attendance_rate', 0.0):.1f}% ({attendance_summary.get('present_days', 0)}/{attendance_summary.get('total_days', 0)} Days)"

    status_color = colors.HexColor('#10B981') if student_summary.get('pass_fail_status') == 'Pass' else colors.HexColor('#EF4444')

    info_data = [
        [
            Paragraph("<b>Student Name:</b>", cell_style), Paragraph(student_name, bold_cell_style),
            Paragraph("<b>Roll Number:</b>", cell_style), Paragraph(str(roll_no), bold_cell_style)
        ],
        [
            Paragraph("<b>Class & Section:</b>", cell_style), Paragraph(class_sec, cell_style),
            Paragraph("<b>Student ID:</b>", cell_style), Paragraph(str(student_id), cell_style)
        ],
        [
            Paragraph("<b>Date of Birth:</b>", cell_style), Paragraph(dob_str, cell_style),
            Paragraph("<b>Attendance:</b>", cell_style), Paragraph(att_rate_str, cell_style)
        ],
        [
            Paragraph("<b>Email:</b>", cell_style), Paragraph(email, cell_style),
            Paragraph("<b>Result Status:</b>", cell_style), 
            Paragraph(f"<b>{student_summary.get('pass_fail_status', 'N/A').upper()}</b>", 
                      ParagraphStyle('Status', parent=cell_style, textColor=status_color, fontName='Helvetica-Bold'))
        ]
    ]

    info_table = Table(info_data, colWidths=[95, 175, 95, 175])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#EDF2F7')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # 3. Performance Summary Overview Metrics (with GPA & CGPA)
    total_obtained = student_summary.get('total_marks_obtained', 0)
    total_max = student_summary.get('total_max_marks', 0)
    percentage = student_summary.get('overall_percentage', 0.0)
    grade = student_summary.get('overall_grade', 'N/A')
    gpa = student_summary.get('gpa', 0.0)
    cgpa = student_summary.get('cgpa', 0.0)

    summary_data = [
        [
            Paragraph("<b>Total Score</b>", cell_style),
            Paragraph("<b>Percentage</b>", cell_style),
            Paragraph("<b>Grade</b>", cell_style),
            Paragraph("<b>GPA (4.0)</b>", cell_style),
            Paragraph("<b>CGPA (10.0)</b>", cell_style)
        ],
        [
            Paragraph(f"<font size=11><b>{total_obtained} / {total_max}</b></font>", bold_cell_style),
            Paragraph(f"<font size=11><b>{percentage:.1f}%</b></font>", bold_cell_style),
            Paragraph(f"<font size=11 color='#4F46E5'><b>{grade}</b></font>", bold_cell_style),
            Paragraph(f"<font size=11><b>{gpa:.2f}</b></font>", bold_cell_style),
            Paragraph(f"<font size=11><b>{cgpa:.2f}</b></font>", bold_cell_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[110, 105, 105, 110, 110])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2FF')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFFFFF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E7FF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # 4. Subject-wise Details Table
    story.append(Paragraph("Subject-Wise Academic Performance & Competencies", section_heading))

    subject_details = student_summary.get('subject_details', [])
    subjects_table_data = [
        [
            Paragraph("<b>#</b>", bold_cell_style),
            Paragraph("<b>Subject Name</b>", bold_cell_style),
            Paragraph("<b>Obtained</b>", bold_cell_style),
            Paragraph("<b>Max</b>", bold_cell_style),
            Paragraph("<b>Percent</b>", bold_cell_style),
            Paragraph("<b>Grade</b>", bold_cell_style),
            Paragraph("<b>Term</b>", bold_cell_style),
            Paragraph("<b>Assessment Type</b>", bold_cell_style)
        ]
    ]

    for idx, subj in enumerate(subject_details, 1):
        p_val = subj.get('percentage', 0.0)
        grade_val = subj.get('grade', 'N/A')
        term_val = subj.get('term', 'Term 1')
        subjects_table_data.append([
            Paragraph(str(idx), cell_style),
            Paragraph(subj.get('subject', 'Unknown'), cell_style),
            Paragraph(str(subj.get('marks_obtained', 0)), cell_style),
            Paragraph(str(subj.get('max_marks', 100)), cell_style),
            Paragraph(f"{p_val:.1f}%", cell_style),
            Paragraph(f"<b>{grade_val}</b>", bold_cell_style),
            Paragraph(term_val, cell_style),
            Paragraph(subj.get('assessment_type', 'Exam'), cell_style)
        ])

    subj_table = Table(subjects_table_data, colWidths=[24, 150, 52, 50, 60, 44, 60, 100])
    subj_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(subj_table)
    story.append(Spacer(1, 14))

    # 5. Teacher Observations & Grading Scale Reference
    remarks = "Outstanding performance! Demonstrates strong conceptual understanding and intellectual rigor." if percentage >= 85 else (
        "Commendable progress! Solid grasp of curriculum; keep aiming for higher distinction." if percentage >= 70 else (
            "Satisfactory standing. Consistent revision and engagement in practice sessions encouraged." if percentage >= 50 else (
                "Borderline academic progress. Structured mentoring and remedial intervention recommended." if percentage >= 40 else
                "Critical intervention required. Immediate counseling and faculty tutorial sessions needed."
            )
        )
    )

    eval_data = [
        [
            Paragraph("<b>Faculty Remarks:</b>", cell_style),
            Paragraph(remarks, cell_style)
        ],
        [
            Paragraph("<b>Standard Scale:</b>", cell_style),
            Paragraph("A+ &ge; 90% (4.0 GPA) &bull; A &ge; 80% (3.7) &bull; B+ &ge; 70% (3.3) &bull; B &ge; 60% (3.0) &bull; C+ &ge; 50% (2.3) &bull; C &ge; 40% (2.0) &bull; F &lt; 40% (0.0)", cell_style)
        ]
    ]
    eval_table = Table(eval_data, colWidths=[105, 435])
    eval_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(eval_table)
    story.append(Spacer(1, 28))

    # 6. Institutional Sign-Off Blocks
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Class Teacher</b>", cell_style),
            Paragraph("____________________________<br/><b>Academic Dean / Principal</b>", cell_style),
            Paragraph("____________________________<br/><b>Parent / Guardian</b>", cell_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether(sig_table))

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_class_report_cards_zip(class_name: str, section: str = None) -> bytes:
    """
    Generate a ZIP archive containing individual PDF report cards for all students in a class.
    
    Args:
        class_name: Class name (e.g. '10')
        section: Optional section filter (e.g. 'A')
        
    Returns:
        bytes: Raw bytes of the generated ZIP file
    """
    from models.student import Student
    from models.marks import Marks
    from models.attendance import Attendance

    students = Student.get_students_by_class(class_name, section)
    if not students:
        return b""

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for st_row in students:
            student_id = st_row[0]
            student_info = Student.get_student_by_id(student_id)
            student_summary = Marks.get_student_summary(student_id)
            attendance_summary = Attendance.get_student_attendance_summary(student_id)

            pdf_bytes = generate_student_report_pdf(student_summary, student_info, attendance_summary)
            
            raw_name = student_info[1] if student_info else f"Student_{student_id}"
            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_name)
            roll_str = str(student_info[5] if len(student_info) > 5 and student_info[5] else student_id)
            filename = f"{clean_name}_{roll_str}_Report_Card.pdf"

            zf.writestr(filename, pdf_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
