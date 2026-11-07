from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Company
from .forms import CompanyForm
from apps.jobs.models import Job, JobApplication


@login_required
def company_dashboard(request):
    if request.user.user_type != 'company' and not request.user.is_superuser:
        messages.error(request, 'Company dashboard is only accessible to recruiters.')
        return redirect('jobs:home')

    company = getattr(request.user, 'company_profile', None)
    if not company:
        messages.info(request, 'Please complete your company profile to start posting jobs.')
        return redirect('companies:create')

    # Fetch jobs with applicant counts
    jobs = company.jobs.all().annotate(total_applicants=Count('jobapplication'))
    
    total_jobs = jobs.count()
    active_jobs = jobs.filter(is_active=True).count()
    
    # Total applicants across all company jobs
    total_applicants = JobApplication.objects.filter(job__company=company).count()
    shortlisted_count = JobApplication.objects.filter(job__company=company, status='shortlisted').count()

    return render(request, 'companies/dashboard.html', {
        'company': company,
        'jobs': jobs,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'shortlisted_count': shortlisted_count,
    })


@login_required
def create_company(request):
    if request.user.user_type != 'company':
        messages.error(request, 'Only company accounts can register company profiles.')
        return redirect('jobs:home')

    if hasattr(request.user, 'company_profile'):
        messages.info(request, 'Company profile already exists. You can update it here.')
        return redirect('companies:edit')

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            messages.success(request, f'Company profile "{company.name}" created successfully!')
            return redirect('companies:dashboard')
    else:
        form = CompanyForm()

    return render(request, 'companies/company_form.html', {'form': form, 'is_edit': False})


@login_required
def edit_company(request):
    company = get_object_or_404(Company, user=request.user)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company details updated successfully!')
            return redirect('companies:dashboard')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/company_form.html', {'form': form, 'company': company, 'is_edit': True})


def company_list(request):
    """Public directory of hiring companies (Fig 4.6 in KTU project report)."""
    query = request.GET.get('q', '').strip()
    industry = request.GET.get('industry', '').strip()

    companies = Company.objects.filter(is_verified=True).annotate(
        active_jobs_count=Count('jobs', filter=Q(jobs__is_active=True))
    )

    if query:
        companies = companies.filter(Q(name__icontains=query) | Q(location__icontains=query) | Q(description__icontains=query))
    if industry:
        companies = companies.filter(industry__iexact=industry)

    # Unique industries for filter dropdown
    industries = Company.objects.values_list('industry', flat=True).distinct()

    return render(request, 'companies/company_list.html', {
        'companies': companies,
        'industries': sorted([i for i in industries if i]),
        'query': query,
        'selected_industry': industry,
    })


def company_detail(request, pk):
    """Company profile and their open positions."""
    company = get_object_or_404(Company, pk=pk)
    open_jobs = company.jobs.filter(is_active=True)

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'open_jobs': open_jobs,
    })
