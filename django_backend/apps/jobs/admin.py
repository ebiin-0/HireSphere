from django.contrib import admin
from .models import Job, JobApplication

class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ['applied_date', 'status']
    fields = ['applicant', 'resume', 'cover_letter', 'status', 'applied_date']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'location', 'experience_level', 'is_active', 'posted_date', 'get_salary_range']
    list_filter = ['job_type', 'experience_level', 'is_active', 'posted_date']
    search_fields = ['title', 'company__name', 'skills_required', 'location']
    list_per_page = 25
    inlines = [JobApplicationInline]
    readonly_fields = ['posted_date']

    fieldsets = (
        ('Job Details', {'fields': ('title', 'company', 'job_type', 'experience_level', 'location', 'posted_date')}),
        ('Compensation & Type', {'fields': ('salary_min', 'salary_max', 'is_active')}),
        ('Description', {'fields': ('description',), 'classes': ('wide',)}),
        ('Requirements', {'fields': ('requirements', 'skills_required'), 'classes': ('wide',)}),
        ('Application Deadline', {'fields': ('deadline',)}),
    )

    def get_salary_range(self, obj):
        return obj.get_salary_range()
    get_salary_range.short_description = 'Salary Range'
    get_salary_range.admin_order_field = 'salary_min'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'applied_date', 'status']
    list_filter = ['status', 'applied_date', 'job__company', 'job__job_type']
    search_fields = ['applicant__username', 'applicant__email', 'job__title']
    list_per_page = 25
    readonly_fields = ['applied_date']
    fieldsets = (
        ('Application Info', {'fields': ('job', 'applicant', 'applied_date')}),
        ('Documents', {'fields': ('resume', 'cover_letter')}),
        ('Status', {'fields': ('status',), 'classes': ('wide',)}),
    )
