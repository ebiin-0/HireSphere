from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPES = (
        ('seeker', 'Job Seeker'),
        ('company', 'Company Recruiter'),
        ('admin', 'Administrator'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='seeker')
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    headline = models.CharField(max_length=150, blank=True, default='')
    education = models.CharField(max_length=200, blank=True, default='')
    experience_years = models.IntegerField(default=0)
    skills = models.TextField(blank=True, default='', help_text="Comma-separated skills declared by user")
    location = models.CharField(max_length=100, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    
    # Resume & ATS Analysis
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_score = models.IntegerField(default=0, help_text="ATS Quality Score 0-100")
    resume_feedback = models.TextField(blank=True, default='', help_text="Recommendations and suggestions")
    
    # Verification & Privacy
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(null=True, blank=True)
    anonymous_in_screening = models.BooleanField(default=True, help_text="Hide personal identifiers during initial screening")

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def candidate_id(self):
        return f"CAN-{self.id:04d}"


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_skills')
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=50, help_text="Skill proficiency level 0-100%")
    is_verified = models.BooleanField(default=False, help_text="True if proven via assessment quiz")
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['-is_verified', '-level', 'name']

    def __str__(self):
        status = "Verified" if self.is_verified else "Self-reported"
        return f"{self.user.username} - {self.name} ({self.level}% - {status})"


class QuizCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fa-code")
    passing_score = models.IntegerField(default=60, help_text="Passing percentage")

    class Meta:
        verbose_name_plural = "Quiz Categories"

    def __str__(self):
        return self.name

    @property
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, default='')

    def __str__(self):
        return f"[{self.category.name}] {self.question[:60]}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    score_percentage = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.score_percentage}%)"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Q{self.question_id}: {self.selected_answer}"
