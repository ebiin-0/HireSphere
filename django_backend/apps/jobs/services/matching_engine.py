"""
Intelligent Job Matching & Skill Gap Analysis Service
HireSphere - Skill Validation and Hiring Platform (KTU B.Tech Mini Project)
"""

import re
from typing import Dict, List, Any


LEARNING_ROADMAPS = {
    "python": "Master Python fundamentals, OOP concepts, list comprehensions, and data processing libraries.",
    "java": "Study Core Java, collections framework, multithreading, and OOP design patterns.",
    "django": "Learn Django MVT architecture, ORM queries, authentication, and REST APIs.",
    "spring boot": "Practice Spring Boot microservices, dependency injection, JPA/Hibernate, and Spring Security.",
    "sql": "Practice SQL queries: INNER/LEFT JOINs, subqueries, indexing, and database normalization.",
    "mysql": "Learn MySQL schema design, query optimization, foreign keys, and transactions.",
    "postgresql": "Practice PostgreSQL advanced data types (JSONB), window functions, and indexing.",
    "react": "Build single-page apps using React functional components, hooks (useState, useEffect), and state management.",
    "javascript": "Master ES6+ syntax, asynchronous programming (Promises, async/await), and DOM manipulation.",
    "docker": "Understand containerization fundamentals, writing Dockerfiles, and orchestrating with Docker Compose.",
    "aws": "Explore cloud essentials: EC2 compute, S3 storage, RDS databases, and IAM security policies.",
    "machine learning": "Learn supervised/unsupervised learning algorithms using Scikit-Learn, Pandas, and NumPy.",
    "git": "Practice Git version control: branching, merging, rebasing, pull requests, and GitHub workflows.",
    "rest api": "Understand HTTP status codes, RESTful resource modeling, request/response headers, and API documentation.",
    "data structures": "Practice arrays, linked lists, stacks, queues, trees, graphs, and Big-O algorithm analysis.",
}


def normalize_skill(name: str) -> str:
    """Normalize skill string for resilient comparison."""
    clean = re.sub(r'[^a-zA-Z0-9+#]', '', name.strip().lower())
    return clean


def compute_job_compatibility(candidate, job) -> Dict[str, Any]:
    """
    Computes compatibility score between candidate skills and job requirements.
    Performs skill gap analysis and returns detailed breakdown.
    """
    required_skills = job.get_skills_list()
    if not required_skills:
        return {
            "score": 75,
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": [],
        }

    # Fetch candidate's skills from Skill model
    candidate_skills = list(candidate.candidate_skills.all())
    # Create normalized lookup dictionary
    cand_skill_map = {normalize_skill(s.name): s for s in candidate_skills}
    
    # Also check candidate's raw comma-separated text skills
    raw_skills = [normalize_skill(s) for s in (candidate.skills or "").split(",") if s.strip()]

    matched = []
    missing = []
    
    total_required = len(required_skills)
    earned_weight = 0.0
    max_weight = float(total_required)

    for req in required_skills:
        norm_req = normalize_skill(req)
        matched_obj = cand_skill_map.get(norm_req)

        if matched_obj:
            is_verified = matched_obj.is_verified
            level = matched_obj.level
            # Verified skills provide a higher weight bonus
            weight = 1.0 if not is_verified else 1.25
            earned_weight += weight
            matched.append({
                "name": req,
                "is_verified": is_verified,
                "level": level,
            })
        elif norm_req in raw_skills:
            earned_weight += 0.85
            matched.append({
                "name": req,
                "is_verified": False,
                "level": 60,
            })
        else:
            missing.append(req)

    # Base match calculation
    raw_percentage = (earned_weight / max_weight) * 100 if max_weight > 0 else 0
    final_score = int(min(100, max(15, round(raw_percentage))))

    # Build recommendations for missing skills
    recommendations = []
    for skill in missing:
        norm_s = skill.lower().strip()
        roadmap = None
        for key, text in LEARNING_ROADMAPS.items():
            if key in norm_s or norm_s in key:
                roadmap = text
                break
        if not roadmap:
            roadmap = f"Study {skill} core concepts and build a hands-on mini project demonstrating competency."

        recommendations.append({
            "skill": skill,
            "roadmap": roadmap,
        })

    return {
        "score": final_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": recommendations,
    }


def update_application_scores(application):
    """Calculates and persists compatibility scores on a JobApplication instance."""
    result = compute_job_compatibility(application.applicant, application.job)
    application.compatibility_score = result["score"]
    application.matched_skills = ", ".join([m["name"] for m in result["matched_skills"]])
    application.missing_skills = ", ".join(result["missing_skills"])
    application.save(update_fields=['compatibility_score', 'matched_skills', 'missing_skills'])
    return result
