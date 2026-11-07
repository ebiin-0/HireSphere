from django.db import models
from django.contrib.auth import get_user_model
from apps.companies.models import Company

User = get_user_model()


class Job(models.Model):
    JOB_TYPES = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    )

    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    requirements = models.TextField()
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full-time')
    location = models.CharField(max_length=200)
    skills_required = models.TextField(help_text="Comma-separated skills (e.g. Python, Django, SQL)")
    experience_level = models.CharField(max_length=50, default='Entry Level')
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    def get_salary_range(self):
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,.0f} - ₹{self.salary_max:,.0f}"
        if self.salary_min:
            return f"₹{self.salary_min:,.0f}+"
        return 'Salary not specified'

    def get_skills_list(self):
        if not self.skills_required:
            return []
        # Support comma, semicolon, newline, slash
        import re
        tokens = re.split(r'[,;/\n]+', self.skills_required)
        return [t.strip() for t in tokens if t.strip()]

    @property
    def applicant_count(self):
        return self.jobapplication_set.count()


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted for Interview'),
        ('rejected', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, default='')
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Automated Matching & Assessment Score
    compatibility_score = models.IntegerField(default=0, help_text="Calculated match percentage 0-100")
    matched_skills = models.TextField(blank=True, default='')
    missing_skills = models.TextField(blank=True, default='')
    recruiter_notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-compatibility_score', '-applied_date']
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title} ({self.compatibility_score}%)"

    def get_matched_skills_list(self):
        if not self.matched_skills:
            return []
        return [s.strip() for s in self.matched_skills.split(',') if s.strip()]

    def get_missing_skills_list(self):
        if not self.missing_skills:
            return []
        return [s.strip() for s in self.missing_skills.split(',') if s.strip()]
