<div align="center">

# 🎓 Student Performance Tracker
### *Enterprise Academic Intelligence & Student Analytics Suite*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing-22C55E.svg?style=for-the-badge&logo=checkmarx&logoColor=white)](tests/test_cases.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A robust, modern, and comprehensive academic performance management system engineered with **Streamlit**, **SQLite**, and **Plotly**. Features real-time institutional analytics, dual grading scales (4.0 GPA & 10.0 UGC/CBSE), attendance correlation engines, ReportLab PDF report cards, and a dual-theme UI engine with high-contrast accessibility.

[🚀 **Launch Live Application**](https://student-performance-tracker-fn7euyfqjuzyksjzbowvvt.streamlit.app/) • [💻 GitHub Repository](https://github.com/gouransh1024/Student-Performance-tracker) • [📖 Documentation](#-table-of-contents) • [⚡ Quick Start](#-quick-start) • [🧪 Run Tests](#-test-suite)

</div>

---

## 🚀 Live Demo

Experience the full enterprise application live on Streamlit Cloud:

👉 **[https://student-performance-tracker-fn7euyfqjuzyksjzbowvvt.streamlit.app/](https://student-performance-tracker-fn7euyfqjuzyksjzbowvvt.streamlit.app/)**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Highlights](#-key-highlights)
- [Core Features](#-core-features)
  - [1. Student Directory & Profile Management](#1-student-directory--profile-management)
  - [2. Curriculum & Subject Architecture](#2-curriculum--subject-architecture)
  - [3. Assessment & Multi-Scale Grading](#3-assessment--multi-scale-grading)
  - [4. Attendance Tracking & Correlation Engine](#4-attendance-tracking--correlation-engine)
  - [5. Official Report Cards & PDF Generation](#5-official-report-cards--pdf-generation)
  - [6. Class-Level & Cohort Visual Analytics](#6-class-level--cohort-visual-analytics)
  - [7. Bulk Data Ingestion Engine](#7-bulk-data-ingestion-engine)
  - [8. System Administration & Sample Generator](#8-system-administration--sample-generator)
- [Design & Dual Theme Engine](#-design--dual-theme-engine)
- [Technical Architecture & Database Schema](#-technical-architecture--database-schema)
- [Grading Engine Standards](#-grading-engine-standards)
- [Installation & Setup](#-installation--setup)
- [Test Suite](#-test-suite)
- [Project Directory Structure](#-project-directory-structure)
- [Screenshots & Visuals](#-screenshots--visuals)
- [Contributing](#-contributing)
- [Author & Contact](#-author--contact)

---

## 🎯 Overview

The **Student Performance Tracker** is designed for high schools, colleges, and educational administrators seeking a lightweight, zero-latency desktop and cloud-ready analytics workstation. Built with modern web standards, it handles student rosters, marks entries, assessment breakdowns, attendance logging, and cohort-level trends without cumbersome cloud setups or recurring subscription tiers.

### 🌟 Key Highlights

- **🌓 Dual Theme Experience**: Native toggle between **Obsidian Slate Dark Mode** and **Pearl Academic Light Mode** with strict WCAG contrast compliance and sidebar glyph protection.
- **📈 Attendance & Academic Correlation**: Interactive Pearson correlation engine visualizing how attendance directly influences student assessment scores.
- **📄 Instant PDF Transcript Generation**: Downloadable formal student report cards powered by ReportLab with subject matrices, GPA conversions, and faculty signature sections.
- **⚖️ Dual GPA Calculation Engine**: Simultaneous calculation of 4.0 US Collegiate GPA and 10.0 UGC/CBSE Scale alongside traditional percentage grades (A+ to F).
- **🛡️ Enterprise Integrity**: SQLite schema enforced with `PRAGMA foreign_keys = ON;`, cascading deletions (`Attendance -> Marks -> Student -> Subject`), and atomic transactions.
- **⚡ Pre-Engineered Sample Datasets**: One-click reset and generation of 10 students across classes 10, 11, and 12 with 150+ assessment records and 20 school days of attendance history.

---

## ✨ Core Features

### 1. Student Directory & Profile Management
- Complete CRUD operations with live search, class filtering (10, 11, 12), and section filtering (A, B, C).
- Roll number indexing (`10A-01`, `11A-01`, etc.), contact details, date of birth, and enrollment timestamps.
- Live export of student records to CSV with single-click actions.

### 2. Curriculum & Subject Architecture
- Dynamic curriculum builder with duplicate-prevention validation.
- Preset subject libraries (Mathematics, Physics, Chemistry, English, Computer Science, Biology, etc.).
- Real-time subject-wise statistics: enrolled student count, average assessment scores, and passing ratios.

### 3. Assessment & Multi-Scale Grading
- Support for varied assessment categories: **Assignment, Quiz, Midterm, Final, Project**.
- Real-time score validation preventing marks greater than maximum values.
- Automated instant letter grading (`A+`, `A`, `B+`, `B`, `C+`, `C`, `F`) and percentage calculations.

### 4. Attendance Tracking & Correlation Engine
- Daily roll-call logging: **Present**, **Late**, **Excused**, and **Absent**.
- Date-range attendance analytics with individual attendance rate KPIs.
- **Academic Correlation Plot**: Scatter analysis with linear regression trendlines indicating whether student attendance rates correlate directly with examination outcomes.

### 5. Official Report Cards & PDF Generation
- Comprehensive student report card view complete with academic GPA, total marks, percentage, and attendance summary.
- **ReportLab PDF Exporter**: Generates clean, printable PDF report cards ready for distribution to students, guardians, and academic counselors.

### 6. Class-Level & Cohort Visual Analytics
- Class-wide and section-wide performance comparison charts with Plotly interactive graphs.
- Subject-wise score distribution boxplots and range visualizations.
- Pass/Fail risk identification matrix highlighting students requiring remedial intervention.
- Class leaderboards and top performer rankings.

### 7. Bulk Data Ingestion Engine
- Bulk ingestion of Students, Subjects, and Assessment Marks via CSV or Excel (`.xlsx`, `.xls`).
- Pre-validated schema parsing with detailed line-by-line syntax and foreign-key validation reporting.
- Ready-to-use downloadable sample CSV templates.

### 8. System Administration & Sample Generator
- System health diagnostic counters for active students, registered subjects, and recorded assessments.
- Institutional database cleanup with cascading deletion protection.
- One-click sample data generation populating authentic students, marks, and attendance records.

---

## 🎨 Design & Dual Theme Engine

The application features a custom UI design system built in [`utils/ui_theme.py`](file:///c:/Users/goura/Downloads/Student-Performance-Tracker-application-main/utils/ui_theme.py):

| Theme Option | Background Palette | Card Surface | Text & Headings | Primary Accent |
| :--- | :--- | :--- | :--- | :--- |
| **🌙 Obsidian Slate Dark** | `#0f172a` (Deep Slate) | `#1e293b` with 1px border | `#f8fafc` & `#94a3b8` | `#6366f1` (Indigo Glow) |
| **☀️ Pearl Academic Light**| `#f8fafc` (Off-white) | `#ffffff` with subtle shadow | `#0f172a` & `#475569` | `#4f46e5` (Royal Indigo) |

### Key UI Features:
- **Zero White-on-White Collisions**: High-contrast calibrated sidebar navigation (`stSidebarNav`) ensuring clear legibility of page names and icons in both modes.
- **Preserved Material Symbols**: Custom font-family locks preventing icon corruption or fallback ligature text.
- **Glassmorphic Metric Cards**: KPI badges featuring subtle borders, glow accents, and responsive flex typography.

---

## 🏗️ Technical Architecture & Database Schema

The database leverages SQLite with relational integrity constraints enforced at connection initialization:

```sql
-- Student Entity
CREATE TABLE Student (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) >= 2),
    class TEXT NOT NULL CHECK(class IN ('10', '11', '12')),
    section TEXT NOT NULL CHECK(section IN ('A', 'B', 'C')),
    dob DATE,
    roll_number TEXT UNIQUE,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subject Entity
CREATE TABLE Subject (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL UNIQUE CHECK(length(trim(subject_name)) >= 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assessment Marks Entity
CREATE TABLE Marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    marks_obtained INTEGER NOT NULL CHECK(marks_obtained >= 0),
    max_marks INTEGER DEFAULT 100 CHECK(max_marks > 0),
    assessment_date DATE DEFAULT (date('now')),
    assessment_type TEXT DEFAULT 'Assignment' 
        CHECK(assessment_type IN ('Quiz', 'Assignment', 'Midterm', 'Final', 'Project')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
    CHECK(marks_obtained <= max_marks)
);

-- Attendance Records Entity
CREATE TABLE Attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    UNIQUE(student_id, date)
);
```

---

## 📊 Grading Engine Standards

The grading calculation engine converts raw marks to standardized institutional scales:

| Percentage Range | Letter Grade | 4.0 Scale GPA | 10.0 Scale Point | Academic Standing |
| :---: | :---: | :---: | :---: | :---: |
| **90% – 100%** | **A+** | 4.00 | 10.0 | Outstanding Honors |
| **80% – 89%** | **A** | 3.75 | 9.0 | Excellent Standing |
| **70% – 79%** | **B+** | 3.25 | 8.0 | Very Good |
| **60% – 69%** | **B** | 3.00 | 7.0 | Good Standing |
| **50% – 59%** | **C+** | 2.50 | 6.0 | Above Average |
| **40% – 49%** | **C** | 2.00 | 5.0 | Average Pass |
| **Below 40%** | **F** | 0.00 | 0.0 | Academic Remediation |

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8 to 3.12+** installed on your system.
- **Git** version control tool.

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/gouransh1024/Student-Performance-tracker.git
   cd Student-Performance-tracker
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access the Interface**
   - Open your browser to `http://localhost:8501`.
   - On the first run, the SQLite database is automatically generated with ready-to-test academic records.

---

## 🧪 Test Suite

The project includes unit test coverage for grading calculations, attendance scoring, and model workflows.

To run the complete test suite:
```bash
python -m unittest tests/test_cases.py
```

### Expected Output:
```text
----------------------------------------------------------------------
Ran 18 tests in 0.812s

OK
```

---

## 📁 Project Directory Structure

```text
Student-Performance-tracker/
├── 📄 app.py                     # Primary dashboard & navigation router
├── 📂 pages/                     # Streamlit multi-page application
│   ├── 1_Manage_Students.py      # Student profile management & directory
│   ├── 2_Manage_Subjects.py      # Curriculum and subject administration
│   ├── 3_Enter_Update_Marks.py   # Assessment marks recording & updates
│   ├── 4_Student_Report_Card.py  # Transcript view with PDF export
│   ├── 5_Class_Analytics.py      # Class comparative analytics
│   ├── 6_Visual_Reports.py       # Plotly distribution charts & trends
│   ├── 7_Settings.py             # Theme settings, diagnostics & sample data
│   ├── 8_Bulk_Data_Import.py     # CSV/Excel bulk file parser
│   └── 9_Attendance_Tracker.py   # Attendance logging & correlation engine
├── 📂 models/                    # Data access layer & business entities
│   ├── student.py                # Student model & query handlers
│   ├── subject.py                # Subject model & query handlers
│   └── marks.py                  # Assessment calculations & marks queries
├── 📂 db/                        # Database management layer
│   └── connection.py             # SQLite schema, pooling & sample dataset generator
├── 📂 utils/                     # Core utility & rendering engine
│   ├── ui_theme.py               # Dual theme engine (Dark/Light CSS injection)
│   ├── data_management.py        # Cascading reset, deletion & verification
│   ├── analytics.py              # Performance calculations & statistical models
│   └── data_import.py            # CSV/XLSX template parser & validators
├── 📂 tests/                     # Automated quality assurance
│   └── test_cases.py             # 18 unit tests covering all calculation logic
├── 📄 requirements.txt           # Production dependencies
├── 📄 install.py                 # Automated dependency installer
└── 📄 Readme.md                  # Institutional documentation
```

---

## 🤝 Contributing

Contributions are warmly welcomed! To contribute:

1. **Fork the Repository**
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/academic-enhancement
   ```
3. **Commit Your Code**:
   ```bash
   git commit -m "feat: add semester-over-semester trend forecasting"
   ```
4. **Push to GitHub**:
   ```bash
   git push origin feature/academic-enhancement
   ```
5. **Open a Pull Request** for review.

---

## 👨‍💻 Author & Contact

**Gouransh Soni**  
*Full Stack Developer & Data Analytics Enthusiast*

- 🌐 **GitHub**: [@gouransh1024](https://github.com/gouransh1024)
- 💼 **LinkedIn**: [Gouransh Soni](https://www.linkedin.com/in/gouransh-soni-3556192b1)
- 📧 **Email**: [gouransh1024@gmail.com](mailto:gouransh1024@gmail.com)
- 📱 **Phone**: [+91 9509682181](tel:+919509682181)
- 🚀 **Live Demo**: [ApexTracker Cloud Application](https://student-performance-tracker-fn7euyfqjuzyksjzbowvvt.streamlit.app/)

---

<div align="center">

*Empowering educational excellence through modern data analytics.* 🎓✨

</div>
