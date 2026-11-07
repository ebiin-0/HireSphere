from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from apps.users.models import User, Skill, QuizAttempt
from apps.companies.models import Company
from apps.jobs.models import Job, JobApplication


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.user_type == 'admin')


@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_dashboard(request):
    candidates = User.objects.filter(user_type='seeker').prefetch_related('candidate_skills')
    companies = Company.objects.all().select_related('user')
    jobs = Job.objects.all().select_related('company').order_by('-posted_date')
    applications = JobApplication.objects.all().select_related('applicant', 'job')

    stats = {
        'total_candidates': candidates.count(),
        'total_companies': companies.count(),
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_applications': applications.count(),
        'verified_skills': Skill.objects.filter(is_verified=True).count(),
        'quiz_attempts': QuizAttempt.objects.count(),
    }

    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'candidates': candidates[:15],
        'companies': companies[:15],
        'jobs': jobs[:15],
        'recent_applications': applications[:10],
    })


@user_passes_test(is_admin, login_url='/accounts/login/')
def toggle_user_verification(request, user_id):
    candidate = get_object_or_404(User, id=user_id)
    candidate.is_verified = not candidate.is_verified
    candidate.save(update_fields=['is_verified'])
    status = "verified" if candidate.is_verified else "unverified"
    messages.success(request, f'Candidate {candidate.username} is now marked as {status}.')
    return redirect('admin_panel:dashboard')


@user_passes_test(is_admin, login_url='/accounts/login/')
def toggle_company_verification(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.is_verified = not company.is_verified
    company.save(update_fields=['is_verified'])
    status = "verified" if company.is_verified else "pending"
    messages.success(request, f'Company {company.name} status updated to {status}.')
    return redirect('admin_panel:dashboard')


@user_passes_test(is_admin, login_url='/accounts/login/')
def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.is_active = not job.is_active
    job.save(update_fields=['is_active'])
    status = "active" if job.is_active else "inactive/closed"
    messages.success(request, f'Job "{job.title}" is now {status}.')
    return redirect('admin_panel:dashboard')
