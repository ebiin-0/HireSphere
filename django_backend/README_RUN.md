# HireSphere &mdash; Skill Validation and Hiring Platform
### APJ Abdul Kalam Technological University (KTU) B.Tech Computer Science and Engineering Mini Project
**Institution:** Mar Baselios Christian College of Engineering and Technology (MBCET), Peermade  
**Team Members:** Ebin Abraham (MBC23CS049), Adishesh L (MBC23CS011), Angel Mary Jose (MBC23CS026), Ardhra Anna Mathews (MBC23CS029)  
**Project Guide:** Prof. Nissu Simon  

---

## 🚀 How to Run the Project

### 1. Open Terminal and Navigate to `django_backend`:
```powershell
cd django_backend
```

### 2. Start the Django Development Server:
```powershell
python manage.py runserver
```

Open your browser and navigate to:
**👉 http://127.0.0.1:8000/**

---

## 🔑 Pre-Configured Demo Accounts (Ready for Viva & Presentation)

| Role | Username | Password | Purpose & Highlights |
| :--- | :--- | :--- | :--- |
| **Job Seeker (Candidate)** | `ebin` | `ebin123` | Pre-loaded B.Tech CSE profile, 85% ATS resume score, verified Python & SQL badges, applied jobs tracking. |
| **Alternative Candidate** | `alex_rivera` | `alex123` | Senior Product Designer profile (Report Fig 4.4). |
| **Company Recruiter (TCS)** | `tcs_demo` | `demo123` | Tata Consultancy Services &mdash; Recruiter dashboard, active job postings, applicant ranking table. |
| **Company Recruiter (Infosys)** | `infosys_demo` | `demo123` | Infosys recruiter portal with live applicants and anonymous mode. |
| **Company Recruiter (Intileo)** | `intileo_demo` | `demo123` | Intileo Technologies software company. |
| **Platform Administrator** | `admin` | `admin123` | Administrative control center, platform metrics, user & company verification toggles. |

---

## 🎯 How to Demonstrate Key Features (Viva Walkthrough)

### 1. Job Seeker & AI Resume Analysis (Report Fig 4.4 & 4.5)
- Sign in as **`ebin`** (password: `ebin123`).
- Go to **My Profile & Resume** (`/users/profile/`).
- Notice the **ATS Resume Score Gauge (85%)**, section completeness indicators, and AI improvement recommendations.
- Upload any PDF resume and click **Analyze** &mdash; text is parsed via `pypdf`, technical skills are automatically extracted and synced into your skills profile, and an updated ATS score is generated!
- View the interactive **Chart.js** skill mastery level graph.

### 2. Skill Validation Quizzes & Verified Badges (Chapter 3.4 & 4.5)
- Go to **Skill Quizzes** (`/users/quizzes/`).
- Quizzes are available across 4 technical domains: **Python**, **Java**, **Web Development**, and **SQL**.
- Click **Start Assessment** &mdash; a 5-minute timed test with multiple-choice questions.
- Submit the test:
  - If score $\ge 60\%$: instantly earns a **Verified Skill Badge** with green tick and mastery level.
  - Generates detailed question-by-question review with solutions and educational explanations.

### 3. Intelligent Job Matching & Skill Gap Analysis (Chapter 3.2 & 3.4)
- Go to **Find Jobs** (`/jobs/`).
- Notice that for the logged-in candidate, each job card displays a live **Compatibility Score** (e.g. `87% Match`).
- Click on any job (e.g. *Python & Django Backend Developer* or *Full Stack Web Engineer*):
  - **Live Skill Compatibility Widget**: Shows overall compatibility %.
  - **Matched Skills**: Lists which required skills you have, highlighting verified ones.
  - **Skill Gaps (Missing Skills)**: Highlights missing requirements.
  - **Curated Learning Roadmap**: Recommends study topics and mini-projects for each missing skill!
- Click **Apply for this Job** &mdash; submits in 1 click using your profile resume.

### 4. Recruiter Dashboard & Anonymous Screening Mode (Report Page 8, 25 & 44)
- Sign in as **`tcs_demo`** (password: `demo123`).
- Go to **Recruiter Portal** (`/companies/dashboard/`).
- View all posted jobs and applicant counts.
- Click **Rank Candidates** on any job:
  - Applicants are ordered descending by **AI Compatibility Score (%)**.
  - **Anonymous Screening Toggle (Blind Hiring)**:
    - When **Active**: Masks candidate name (`Candidate #CAN-0001`), masks phone and email (`***@***.***`), and hides profile photo. Recruiters evaluate applicants purely based on objective merit, test scores, verified skills, and experience!
    - Click **Reveal Names** to unmask candidate personal contact info when moving them to the interview stage.
  - Change hiring status: *Pending*, *Shortlisted*, *Accepted for Interview*, *Rejected*.

### 5. Companies Directory (Report Fig 4.6)
- Go to **Companies** (`/companies/directory/`).
- Search by company name or filter by industry (*IT Services*, *Software Products*, *Consulting*).
- Click on any company to view their detailed corporate overview and open positions.

### 6. Admin Panel & Moderation (Chapter 3.4.3)
- Sign in as **`admin`** (password: `admin123`).
- Go to **Admin Dashboard** (`/admin-panel/`).
- Real-time platform analytics: Total Candidates, Companies, Live Jobs, Total Applications, Verified Skills, and Quizzes completed.
- One-click verification toggles for candidates and companies.

---

## 🛠️ Technology Stack
- **Backend:** Python, Django 6.x (MVT Architecture)
- **Database:** SQLite (Relational DB, zero-config, pre-populated)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, FontAwesome 6
- **Resume Processing:** `pypdf` (Automated text extraction & ATS scoring)
- **Algorithm:** Weighted Skill Matching & Skill Gap Analysis Engine
