from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'industry', 'location', 'description', 'logo', 'founded_year', 'employee_count']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}
