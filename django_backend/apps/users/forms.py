from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Skill


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    phone = forms.CharField(max_length=15, required=False, label="Phone Number")
    user_type = forms.ChoiceField(
        choices=[
            ('seeker', 'Job Seeker (Candidate)'),
            ('company', 'Recruiter / Employer (Company)'),
        ],
        label="I want to register as"
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'user_type', 'password1', 'password2')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'headline', 'education', 'experience_years', 'location',
            'skills', 'bio', 'profile_picture', 'resume', 'anonymous_in_screening'
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'placeholder': 'e.g. Full Stack Developer | Python Enthusiast'}),
            'education': forms.TextInput(attrs={'placeholder': 'e.g. B.Tech in Computer Science and Engineering, KTU'}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, SQL, React, Docker'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief summary of your professional background and interests'}),
        }


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['resume']
