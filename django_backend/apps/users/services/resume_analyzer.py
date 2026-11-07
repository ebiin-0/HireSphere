"""
Resume Analyzer Service for HireSphere
Skill Validation and Hiring Platform (KTU B.Tech Mini Project)
"""

import re
from typing import Dict, List, Tuple, Any


# Standard technical skills dictionary for matching
CANONICAL_SKILLS = [
    # Languages
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "PHP", "Ruby", "Go", "Rust", "Kotlin", "Swift", "R",
    # Web & Frameworks
    "Django", "Flask", "FastAPI", "Spring Boot", "Spring", "Hibernate", "React", "Angular", "Vue.js", "Node.js", "Express",
    "HTML", "CSS", "Tailwind CSS", "Bootstrap", "jQuery", "Next.js", "ASP.NET",
    # Databases & Big Data
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Oracle", "Cassandra", "Firebase",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "Git", "GitHub", "CI/CD", "Jenkins", "DevOps",
    # AI & Data Science
    "Machine Learning", "Deep Learning", "Data Analysis", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "NLP",
    # Methodologies & Architecture
    "REST API", "GraphQL", "Microservices", "System Design", "Data Structures", "Algorithms", "Agile", "Scrum", "OOP", "Unit Testing",
]

# Patterns for sections in standard resumes
SECTION_PATTERNS = {
    "education": r"(?i)\b(education|academic|qualifications|degree|b\.?tech|b\.?e|m\.?tech|bca|mca)\b",
    "experience": r"(?i)\b(experience|work history|employment|internship|professional experience)\b",
    "projects": r"(?i)\b(projects|academic projects|personal projects|key projects)\b",
    "skills": r"(?i)\b(skills|technical skills|technologies|competencies|core competencies)\b",
    "certifications": r"(?i)\b(certifications|certificates|courses|achievements|awards)\b",
    "contact": r"(?i)\b(contact|email|phone|mobile|address|linkedin|github)\b",
}


def extract_text_from_pdf(file_obj) -> str:
    """Extract text from uploaded PDF resume file."""
    text = ""
    # Try pypdf first
    try:
        from pypdf import PdfReader
        # Rewind if file is file-like
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        reader = PdfReader(file_obj)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass

    # Try PyMuPDF (fitz) fallback
    try:
        import fitz
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        # If file_obj has read()
        if hasattr(file_obj, 'read'):
            stream = file_obj.read()
            doc = fitz.open(stream=stream, filetype="pdf")
        elif isinstance(file_obj, str):
            doc = fitz.open(file_obj)
        else:
            doc = fitz.open(file_obj.path)
            
        for page in doc:
            text += page.get_text() + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass

    return text


def analyze_resume_text(text: str) -> Dict[str, Any]:
    """
    Evaluates resume text for ATS standards, section structure, and technical skills.
    Returns calculated score, found skills, and actionable feedback.
    """
    if not text or len(text.strip()) < 30:
        return {
            "score": 20,
            "skills_found": [],
            "sections_detected": [],
            "feedback": (
                "• The resume appears very short or text could not be clearly extracted.\n"
                "• Ensure your PDF is text-selectable and not a scanned image.\n"
                "• Include dedicated sections for Skills, Education, Projects, and Experience."
            )
        }

    lower_text = text.lower()
    
    # 1. Detect technical skills
    skills_found = []
    for skill in CANONICAL_SKILLS:
        # Match word boundary
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, lower_text):
            skills_found.append(skill)

    # 2. Check sections
    sections_detected = []
    for section_name, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, lower_text):
            sections_detected.append(section_name)

    # 3. Check contact & links
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    has_github = "github.com" in lower_text or "github" in lower_text
    has_linkedin = "linkedin.com" in lower_text or "linkedin" in lower_text

    # 4. Calculate ATS Score (0 - 100)
    score = 0

    # Section completeness: up to 35 points
    section_weights = {
        "skills": 10,
        "education": 8,
        "projects": 7,
        "experience": 6,
        "certifications": 4,
    }
    for sec, pts in section_weights.items():
        if sec in sections_detected:
            score += pts

    # Skills diversity & depth: up to 35 points
    skill_count = len(skills_found)
    if skill_count >= 10:
        score += 35
    elif skill_count >= 7:
        score += 28
    elif skill_count >= 5:
        score += 22
    elif skill_count >= 3:
        score += 15
    elif skill_count >= 1:
        score += 8

    # Contact & links: up to 15 points
    if has_email:
        score += 4
    if has_phone:
        score += 3
    if has_github:
        score += 4
    if has_linkedin:
        score += 4

    # Length & content density: up to 15 points
    words = len(text.split())
    if 250 <= words <= 1200:
        score += 15
    elif 150 <= words < 250 or 1200 < words <= 2000:
        score += 10
    else:
        score += 5

    score = max(25, min(100, score))

    # 5. Generate tailored feedback
    feedback_points = []
    if "skills" not in sections_detected or len(skills_found) < 5:
        feedback_points.append("• Add a clear 'Technical Skills' section categorizing languages, frameworks, and tools.")
    if not has_github and not has_linkedin:
        feedback_points.append("• Include clickable links to your GitHub profile and LinkedIn network.")
    if "projects" not in sections_detected:
        feedback_points.append("• Highlight 2-3 prominent academic or personal projects with technologies used.")
    if "certifications" not in sections_detected:
        feedback_points.append("• Include certifications or online courses (e.g., NPTEL, Coursera, AWS, HackerRank).")
    
    feedback_points.append("• Take HireSphere skill validation quizzes to earn verified badges for your top skills.")
    feedback_points.append("• Use action verbs (e.g. 'Developed', 'Engineered', 'Optimized') and measurable results.")

    return {
        "score": score,
        "skills_found": skills_found,
        "sections_detected": sections_detected,
        "feedback": "\n".join(feedback_points),
    }


def process_resume_for_user(user, resume_file=None):
    """
    Analyzes resume file (or existing uploaded resume on user model),
    computes score, updates user model, and synchronizes Skill models.
    """
    from apps.users.models import Skill
    from django.utils import timezone

    target_file = resume_file or user.resume
    if not target_file:
        return 0, []

    text = extract_text_from_pdf(target_file)
    analysis = analyze_resume_text(text)

    score = analysis["score"]
    skills_found = analysis["skills_found"]
    feedback = analysis["feedback"]

    # Update User model fields
    user.resume_score = score
    user.resume_feedback = feedback
    
    # Merge existing skills with found skills
    existing_skills = [s.strip() for s in (user.skills or "").split(",") if s.strip()]
    all_skills = sorted(list(set(existing_skills + skills_found)))
    user.skills = ", ".join(all_skills)
    user.save(update_fields=['resume_score', 'resume_feedback', 'skills'])

    # Sync Skill models for candidate
    for skill_name in skills_found:
        skill_obj, created = Skill.objects.get_or_create(
            user=user,
            name=skill_name,
            defaults={"level": 60, "is_verified": False}
        )

    return score, skills_found
