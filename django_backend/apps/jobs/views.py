from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from .services.matching_engine import compute_job_compatibility, update_application_scores
from apps.companies.models import Company


def home(request):
    jobs_queryset = Job.objects.filter(is_active=True).select_related('company')
    
    # Query filters
    query = request.GET.get('q')
    job_type = request.GET.get('job_type')
    location = request.GET.get('location')

    if query:
        jobs_queryset = jobs_queryset.filter(
            Q(title__icontains=query) |
            Q(company__name__icontains=query) |
            Q(skills_required__icontains=query)
        )
    if job_type:
        jobs_queryset = jobs_queryset.filter(job_type=job_type)
    if location:
        jobs_queryset = jobs_queryset.filter(location__icontains=location)

    # Top companies for showcase
    featured_companies = Company.objects.filter(is_verified=True)[:6]

    paginator = Paginator(jobs_queryset, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Genuine matching calculation based on skills overlap
    user = request.user
    if user.is_authenticated and user.user_type == 'seeker':
        applied_job_ids = set(JobApplication.objects.filter(applicant=user).values_list('job_id', flat=True))
        for job in page_obj:
            comp = compute_job_compatibility(user, job)
            job.user_match_score = comp['score']
            job.matched_skills = [m['name'] for m in comp.get('matched_skills', [])]
            job.missing_skills = comp.get('missing_skills', [])
            job.has_applied = job.id in applied_job_ids
    else:
        # Default preview candidate profile skills (Alex Rivera: UI/UX, Python, React, SQL, etc.)
        preview_skills = ['Python', 'React', 'HTML', 'CSS', 'SQL', 'Git', 'JavaScript', 'Docker']
        for job in page_obj:
            reqs = job.get_skills_list()
            matched = [s for s in reqs if any(s.lower() == ps.lower() or ps.lower() in s.lower() for ps in preview_skills)]
            missing = [s for s in reqs if not any(s.lower() == ps.lower() or ps.lower() in s.lower() for ps in preview_skills)]
            raw = (len(matched) / len(reqs) * 100) if reqs else 70
            bonus = min(10, len(matched) * 2)
            job.user_match_score = min(100, max(25, round(raw + bonus))) if matched else round(raw)
            job.matched_skills = matched
            job.missing_skills = missing
            job.has_applied = False

    return render(request, 'jobs/home.html', {
        'page_obj': page_obj,
        'featured_companies': featured_companies,
        'Job': Job,
        'query': query or '',
        'job_type': job_type or '',
        'location': location or '',
    })


def job_list(request):
    return home(request)


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)
    user = request.user
    application = None
    compatibility_data = None

    if user.is_authenticated:
        if user.user_type == 'seeker':
            application = JobApplication.objects.filter(job=job, applicant=user).first()
            compatibility_data = compute_job_compatibility(user, job)

    skills_list = job.get_skills_list()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'application': application,
        'compatibility': compatibility_data,
        'skills_list': skills_list,
    })


@login_required
def create_job(request):
    if request.user.user_type != 'company':
        messages.error(request, 'Only company recruiters can post job openings.')
        return redirect('jobs:home')

    company = getattr(request.user, 'company_profile', None)
    if not company:
        messages.warning(request, 'Please create your company profile before posting a job.')
        return redirect('companies:create')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()
            messages.success(request, f'Job posting "{job.title}" has been published successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()

    return render(request, 'jobs/job_form.html', {'form': form, 'is_edit': False})


@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.user != job.company.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this job.')
        return redirect('jobs:job_detail', pk=pk)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job details updated successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_form.html', {'form': form, 'job': job, 'is_edit': True})


@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    user = request.user

    if user.user_type != 'seeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('jobs:job_detail', pk=pk)

    if JobApplication.objects.filter(job=job, applicant=user).exists():
        messages.info(request, 'You have already submitted an application for this position.')
        return redirect('jobs:job_detail', pk=pk)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = user
            
            # Use profile resume if not explicitly uploaded in form
            if not application.resume and user.resume:
                application.resume = user.resume

            application.save()
            # Calculate match score & skill gap
            update_application_scores(application)

            messages.success(
                request,
                f'Application submitted successfully! Your compatibility score is {application.compatibility_score}%.'
            )
            return redirect('jobs:job_detail', pk=pk)
    else:
        # Pre-populate with user resume if available
        initial = {}
        if user.resume:
            initial['resume'] = user.resume
        form = JobApplicationForm(initial=initial)

    compatibility = compute_job_compatibility(user, job)

    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job,
        'compatibility': compatibility,
    })


@login_required
def manage_applicants(request, pk):
    """
    Recruiter Candidate Ranking & Review Dashboard
    Includes Anonymous Screening Mode toggle to eliminate bias.
    """
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)

    # Ensure current user is the company owner or admin
    if request.user != job.company.user and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('jobs:home')

    # Toggle anonymous screening mode (default True for fair blind evaluation)
    anonymous_param = request.GET.get('anonymous')
    if anonymous_param is not None:
        anonymous_mode = (anonymous_param == '1')
        request.session['anonymous_mode'] = anonymous_mode
    else:
        anonymous_mode = request.session.get('anonymous_mode', True)

    applications = job.jobapplication_set.select_related('applicant').all().order_by('-compatibility_score', '-applied_date')

    # Ensure compatibility scores are calculated
    for app in applications:
        if app.compatibility_score == 0:
            update_application_scores(app)

    return render(request, 'jobs/applicants.html', {
        'job': job,
        'applications': applications,
        'anonymous_mode': anonymous_mode,
    })


@login_required
def update_application_status(request, pk):
    """Update applicant hiring pipeline status."""
    application = get_object_or_404(JobApplication.objects.select_related('job', 'job__company'), pk=pk)
    job = application.job

    if request.user != job.company.user and not request.user.is_superuser:
        messages.error(request, 'Unauthorized access.')
        return redirect('jobs:home')

    new_status = request.POST.get('status')
    if new_status in dict(JobApplication.STATUS_CHOICES):
        application.status = new_status
        application.recruiter_notes = request.POST.get('notes', '')
        application.save(update_fields=['status', 'recruiter_notes'])
        messages.success(request, f'Status updated to "{application.get_status_display()}".')

    return redirect('jobs:manage_applicants', pk=job.pk)


def api_jobs_list(request):
    """
    JSON API for live job listings with genuine matching scores.
    Allows frontend clients to query live Django database records.
    """
    from django.http import JsonResponse
    jobs_queryset = Job.objects.filter(is_active=True).select_related('company')
    query = request.GET.get('q')
    location = request.GET.get('location')
    if query:
        jobs_queryset = jobs_queryset.filter(
            Q(title__icontains=query) |
            Q(company__name__icontains=query) |
            Q(skills_required__icontains=query)
        )
    if location:
        jobs_queryset = jobs_queryset.filter(location__icontains=location)
        
    user = request.user
    preview_skills = ['Python', 'React', 'HTML', 'CSS', 'SQL', 'Git', 'JavaScript', 'Docker']
    results = []
    
    for job in jobs_queryset:
        if user.is_authenticated and user.user_type == 'seeker':
            comp = compute_job_compatibility(user, job)
            score = comp['score']
            matched = [m['name'] for m in comp.get('matched_skills', [])]
            missing = comp.get('missing_skills', [])
        else:
            reqs = job.get_skills_list()
            matched = [s for s in reqs if any(s.lower() == ps.lower() or ps.lower() in s.lower() for ps in preview_skills)]
            missing = [s for s in reqs if not any(s.lower() == ps.lower() or ps.lower() in s.lower() for ps in preview_skills)]
            raw = (len(matched) / len(reqs) * 100) if reqs else 70
            bonus = min(10, len(matched) * 2)
            score = min(100, max(25, round(raw + bonus))) if matched else round(raw)

        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.company.name,
            'company_logo': job.company.get_logo_url(),
            'location': job.location,
            'job_type': job.get_job_type_display(),
            'experience': job.experience_level,
            'salary': job.get_salary_range(),
            'skills': job.get_skills_list(),
            'description': job.description,
            'posted': job.posted_date.strftime('%b %d, %Y'),
            'match_score': score,
            'matched_skills': matched,
            'missing_skills': missing,
        })

    response = JsonResponse({'status': 'ok', 'count': len(results), 'jobs': results})
    response['Access-Control-Allow-Origin'] = '*'
    return response
