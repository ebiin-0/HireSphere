# HireSphere &mdash; Intelligent Career Orchestration Platform
### APJ Abdul Kalam Technological University (KTU) B.Tech CSE Mini Project
**Institution:** Mar Baselios Christian College of Engineering and Technology (MBCET), Peermade  
**Team Members:** Ebin Abraham (MBC23CS049), Adishesh L (MBC23CS011), Angel Mary Jose (MBC23CS026), Ardhra Anna Mathews (MBC23CS029)  
**Project Guide:** Prof. Nissu Simon  

---

## 📁 VS Code Project Structure

```
HireSphere/
├── .vscode/                     # VS Code IDE Configuration
│   ├── settings.json            # Pylance python paths, template associations, clean exclusions
│   ├── launch.json              # F5 Debugger profiles (Run Server, Run Tests, Current File)
│   ├── tasks.json               # VS Code build/run tasks (Start Server, Run Tests, Migrate)
│   └── extensions.json          # Recommended extensions (Python, Django, Pylance)
│
├── django_backend/              # Full-Stack Django Core Application
│   ├── apps/                    # Modular Django apps
│   │   ├── users/               # Candidate profile, ATS resume analyzer, auth
│   │   ├── jobs/                # Jobs board, matching engine, application workflow
│   │   ├── companies/           # Company profiles, recruiter portal, blind screening
│   │   ├── quizzes/             # Verified skill assessment engine
│   │   └── admin_panel/         # Administrative dashboard and verification
│   ├── sk_platform/             # Project settings, URLs, WSGI
│   ├── static/                  # Static assets (CSS, JS, SVG company logos)
│   ├── templates/               # Base template with 3D celestial sphere & dark mode
│   ├── media/                   # User uploads (PDF resumes, avatars)
│   ├── db.sqlite3               # Pre-populated SQLite database
│   ├── manage.py                # Django CLI management script
│   └── test_all_features.py     # 6-suite automated verification tests
│
├── frontend/                    # Standalone KTU Report UI Showcase Screens
│   ├── index.html               # Main showcase landing page
│   ├── home.html                # Interactive home screen
│   ├── companies.html           # Partner directory & recruiter view (Fig 4.6)
│   ├── profile.html             # Candidate profile & ATS gauge (Fig 4.4 & 4.5)
│   ├── quiz.html                # Skill assessment UI
│   ├── quiz_result.html         # Test results & badge UI
│   ├── register.html            # Candidate registration (Fig 4.3)
│   └── img/                     # Report asset images & logos
│
├── docs/                        # Project Documentation & Extraction
│   ├── report 4.pdf             # Official KTU Mini Project Report
│   ├── crop_assets.py           # Asset cropping script
│   └── extract_report_assets.py # Report image extraction tool
│
├── archives/                    # Backup Archives & Legacy Code
│   ├── django_backend.zip       # Original backup zip
│   ├── django_backend 1.zip     # Original backup zip
│   ├── full_users_integration-1.zip
│   └── legacy_prototype/        # Initial single-file models/views (Oct 25)
│
├── .gitignore                   # Git ignore rules for Python, Django & VS Code
├── index.html                   # Project launchpad gateway
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
└── RUN_PROJECT.bat              # One-click desktop launcher
```

---

## ⚡ How to Run in VS Code

### Method 1: Using VS Code Run & Debug (F5)
1. Open this folder in **Visual Studio Code**.
2. Press **`F5`** (or go to **Run and Debug** menu).
3. Select **"Django: Run Server (Port 8000)"**.
4. Open your browser at **http://127.0.0.1:8000/**.

### Method 2: Using VS Code Tasks (`Ctrl+Shift+B`)
1. Press **`Ctrl + Shift + B`** (or **Terminal &rarr; Run Build Task...**).
2. Click **"Start Django Server"**.

### Method 3: Using the Integrated Terminal
Open the VS Code Terminal (`Ctrl + ~`) and run:
```powershell
python manage.py runserver 127.0.0.1:8000
```
*(The terminal is pre-configured to open in `django_backend` automatically).*

### Method 4: One-Click Desktop Launcher
Double-click [**`RUN_PROJECT.bat`**](RUN_PROJECT.bat) to start the server and open the browser.

---

## 🔑 Pre-Configured Demo Accounts (Ready for Presentation & Viva)

| Role | Username | Password | Features to Demonstrate |
| :--- | :--- | :--- | :--- |
| **Job Seeker (Candidate)** | **`ebin`** | **`ebin123`** | AI Resume ATS score (85%), skill mastery chart, verified badges, matching engine, 1-click apply |
| **Alternative Candidate** | **`alex_rivera`** | **`alex123`** | Product designer candidate profile |
| **Company Recruiter (TCS)** | **`tcs_demo`** | **`demo123`** | Recruiter portal, applicant rankings, blind screening toggle |
| **Company Recruiter (Infosys)** | **`infosys_demo`** | **`demo123`** | Active vacancies and applicant reviews |
| **Company Recruiter (Intileo)** | **`intileo_demo`** | **`demo123`** | Software product engineering listings |
| **Administrator** | **`admin`** | **`admin123`** | Platform analytics dashboard (`/admin-panel/`) |

---

## 🧪 Running Automated Verification Tests
In VS Code, run:
```powershell
python test_all_features.py
```
Or run the task **"Run KTU Test Suite"** via **Terminal &rarr; Run Task...**.
All 6 suites verify the matching engine, ATS analyzer, endpoints, candidate flow, blind screening recruiter mode, and admin panel.
