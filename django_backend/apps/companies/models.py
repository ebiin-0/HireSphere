from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True, default='')
    industry = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    employee_count = models.CharField(max_length=50, blank=True, default='')
    is_verified = models.BooleanField(default=True, help_text="Admin verified employer")

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def get_active_jobs_count(self):
        return self.jobs.filter(is_active=True).count()

    def get_logo_url(self):
        if self.logo:
            try:
                return self.logo.url
            except Exception:
                pass
        name_lower = self.name.lower()
        if 'tata' in name_lower or 'tcs' in name_lower:
            return '/static/img/company_logos/tcs.svg'
        elif 'infosys' in name_lower:
            return '/static/img/company_logos/infosys.svg'
        elif 'intileo' in name_lower:
            return '/static/img/company_logos/intileo.svg'
        return None
