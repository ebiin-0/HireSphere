import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk_platform.settings')
django.setup()

from django.test import Client
from apps.users.models import User, Skill, QuizCategory, Question, QuizAttempt
from apps.jobs.models import Job, JobApplication
from apps.companies.models import Company
from apps.jobs.services.matching_engine import compute_job_compatibility
from apps.users.services.resume_analyzer import analyze_resume_text

def run_tests():
    print("========================================")
    print("HIRESPHERE KTU MINI PROJECT TEST SUITE")
    print("========================================")

    # 1. Test Matching Engine & Skill Gap Analysis
    ebin = User.objects.get(username='ebin')
    job = Job.objects.filter(title__icontains='Python').first()
    print(f"\n[1] Testing Matching Engine for user '{ebin.username}' and job '{job.title}':")
    comp = compute_job_compatibility(ebin, job)
    print(f"    Compatibility Score: {comp['score']}%")
    print(f"    Matched Skills: {[m['name'] for m in comp['matched_skills']]}")
    print(f"    Missing Skills: {comp['missing_skills']}")
    assert comp['score'] >= 70, "Expected high match for Python developer"
    print("    >>> MATCHING ENGINE TEST PASSED!")

    # 2. Test Resume Analyzer Text Processing & Scoring
    print("\n[2] Testing Resume Analyzer Text Evaluation:")
    sample_resume = """
    EBIN ABRAHAM
    Email: ebin@example.com | Phone: +91 94471 23456 | GitHub: github.com/ebin | LinkedIn: linkedin.com/in/ebin
    EDUCATION
    Bachelor of Technology in Computer Science and Engineering, APJ Abdul Kalam Technological University
    SKILLS
    Python, Django, SQL, PostgreSQL, React, JavaScript, HTML, CSS, Git, Docker, REST API
    EXPERIENCE & PROJECTS
    Full Stack Developer Intern - Built scalable REST APIs using Django and PostgreSQL.
    Developed Skill Validation and Hiring Platform featuring automated ATS resume analysis and skill quizzes.
    CERTIFICATIONS
    Python for Data Science (NPTEL), Complete Django Masterclass
    """
    analysis = analyze_resume_text(sample_resume)
    print(f"    ATS Quality Score: {analysis['score']}%")
    print(f"    Skills Extracted: {analysis['skills_found']}")
    print(f"    Sections Detected: {analysis['sections_detected']}")
    assert analysis['score'] >= 80, "Expected >= 80% for full resume"
    assert "Python" in analysis['skills_found']
    assert "Django" in analysis['skills_found']
    assert "SQL" in analysis['skills_found']
    print("    >>> RESUME ANALYZER TEST PASSED!")

    # 3. Test HTTP Routes with Django Test Client
    client = Client()

    routes_to_test = [
        ('/', 200, "Landing Page"),
        ('/jobs/', 200, "Jobs Board / Home"),
        ('/companies/directory/', 200, "Companies Directory"),
        ('/users/register/', 200, "Candidate Register"),
        ('/accounts/login/', 200, "Login Page"),
        (f'/jobs/{job.pk}/', 200, "Job Detail Page"),
    ]

    print("\n[3] Testing Public Web Endpoints:")
    for path, expected_status, name in routes_to_test:
        resp = client.get(path)
        print(f"    GET {path:26} [{resp.status_code}] - {name}")
        assert resp.status_code == expected_status, f"Failed on {path}: got {resp.status_code}"
    print("    >>> PUBLIC ENDPOINTS PASSED!")

    # 4. Test Authenticated Job Seeker Flow
    print("\n[4] Testing Job Seeker Authenticated Flow:")
    client.force_login(ebin)
    
    seeker_routes = [
        ('/users/profile/', 200, "Profile & Verified Badges"),
        ('/users/quizzes/', 200, "Skill Quizzes Catalog"),
        ('/users/my-applications/', 200, "Candidate Application Tracker"),
    ]
    for path, expected_status, name in seeker_routes:
        resp = client.get(path)
        print(f"    GET {path:26} [{resp.status_code}] - {name}")
        assert resp.status_code == expected_status

    # Test Taking a Quiz
    py_cat = QuizCategory.objects.get(name='Python')
    quiz_resp = client.get(f'/users/quizzes/{py_cat.id}/take/')
    print(f"    GET /users/quizzes/{py_cat.id}/take/ [{quiz_resp.status_code}] - Take Python Quiz")
    assert quiz_resp.status_code == 200

    # Submit quiz answers
    post_data = {}
    for q in py_cat.questions.all():
        post_data[f'question_{q.id}'] = q.correct_answer
    submit_resp = client.post(f'/users/quizzes/{py_cat.id}/take/', data=post_data, follow=True)
    print(f"    POST Python Quiz Answers   [{submit_resp.status_code}] - Submitted Quiz with 100% Score")
    assert submit_resp.status_code == 200
    latest_attempt = ebin.quiz_attempts.first()
    assert latest_attempt.score_percentage == 100
    assert latest_attempt.passed is True
    print(f"    Verified Skill Level Updated: {ebin.candidate_skills.get(name='Python').level}%")
    print("    >>> JOB SEEKER FLOW PASSED!")

    # 5. Test Authenticated Recruiter Flow & Anonymous Screening
    print("\n[5] Testing Recruiter Flow & Anonymous Screening Mode:")
    recruiter_user = job.company.user
    client.force_login(recruiter_user)

    recruiter_routes = [
        ('/companies/dashboard/', 200, "Company Dashboard"),
        (f'/jobs/{job.pk}/applicants/', 200, "Applicant Ranking Table (Anonymous ON)"),
        (f'/jobs/{job.pk}/applicants/?anonymous=0', 200, "Applicant Ranking Table (Anonymous OFF)"),
        ('/jobs/create/', 200, "Create Job Form"),
    ]
    for path, expected_status, name in recruiter_routes:
        resp = client.get(path)
        print(f"    GET {path:36} [{resp.status_code}] - {name}")
        assert resp.status_code == expected_status

    # Check that in anonymous mode, candidate name is masked
    anon_resp = client.get(f'/jobs/{job.pk}/applicants/?anonymous=1')
    assert "CAN-000" in anon_resp.content.decode('utf-8')
    assert "Blind Evaluation Active" in anon_resp.content.decode('utf-8')
    print("    >>> ANONYMOUS SCREENING VERIFIED: Candidate personal identifiers are masked!")

    # 6. Test Admin Panel Flow
    print("\n[6] Testing Admin Panel Flow:")
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)

    admin_resp = client.get('/admin-panel/')
    print(f"    GET /admin-panel/                  [{admin_resp.status_code}] - Admin Dashboard")
    assert admin_resp.status_code == 200
    assert "Platform Administration & Analytics" in admin_resp.content.decode('utf-8')
    print("    >>> ADMIN PANEL PASSED!")

    print("\n========================================")
    print("ALL KTU MINI PROJECT TEST SUITES PASSED!")
    print("========================================")

if __name__ == '__main__':
    run_tests()
