from django import forms
from .models import Job, JobApplication

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'salary_min', 'salary_max', 'job_type', 'location', 'skills_required', 'experience_level', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'skills_required': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']
        widgets = {'cover_letter': forms.Textarea(attrs={'rows': 4})}
