from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, Skill, QuizCategory, Question, QuizAttempt, UserAnswer
from .forms import UserRegistrationForm, UserProfileForm, ResumeUploadForm
from .services.resume_analyzer import process_resume_for_user


def register(request):
    if request.user.is_authenticated:
        return redirect('jobs:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Welcome to HireSphere, {user.first_name or user.username}! Your account has been created.')
            login(request, user)
            if user.user_type == 'company':
                return redirect('companies:create')
            return redirect('users:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    resume_form = ResumeUploadForm(instance=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            saved_user = form.save()
            
            # If a new resume was uploaded during profile update, analyze it automatically
            if 'resume' in request.FILES:
                score, skills_found = process_resume_for_user(saved_user)
                messages.success(
                    request,
                    f'Profile & Resume updated! Resume Quality Score: {score}%. '
                    f'Found {len(skills_found)} technical skills.'
                )
            else:
                messages.success(request, 'Profile details updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=user)

    # Fetch candidate's skills
    skills = user.candidate_skills.all().order_by('-is_verified', '-level', 'name')
    verified_skills = skills.filter(is_verified=True)
    unverified_skills = skills.filter(is_verified=False)

    # Chart data preparation
    skill_labels = [s.name for s in skills[:10]]
    skill_levels = [s.level for s in skills[:10]]

    # Recent quiz attempts
    recent_quizzes = user.quiz_attempts.select_related('category')[:5]

    context = {
        'form': form,
        'resume_form': resume_form,
        'skills': skills,
        'verified_skills': verified_skills,
        'unverified_skills': unverified_skills,
        'skill_labels': skill_labels,
        'skill_levels': skill_levels,
        'recent_quizzes': recent_quizzes,
    }
    return render(request, 'users/profile.html', context)


@login_required
def analyze_resume_now(request):
    """Triggers analysis of user's uploaded resume."""
    user = request.user
    if request.method == 'POST' and 'resume' in request.FILES:
        user.resume = request.FILES['resume']
        user.save(update_fields=['resume'])

    if not user.resume:
        messages.warning(request, 'Please upload a PDF resume first to run the analysis.')
        return redirect('users:profile')

    score, skills_found = process_resume_for_user(user)
    messages.success(
        request,
        f'Resume analysis completed! ATS Quality Score: {score}%. '
        f'Extracted {len(skills_found)} technical skills.'
    )
    return redirect('users:profile')


@login_required
def quiz_catalog(request):
    """Lists all available domain skill assessment quizzes."""
    categories = QuizCategory.objects.all().prefetch_related('questions')
    user = request.user
    
    # Map user's attempts per category
    user_status = {}
    attempts = QuizAttempt.objects.filter(user=user)
    for a in attempts:
        cid = a.category_id
        if cid not in user_status or a.score_percentage > user_status[cid]['best_score']:
            user_status[cid] = {
                'best_score': a.score_percentage,
                'passed': a.passed,
                'attempted_at': a.created_at,
            }

    category_cards = []
    for cat in categories:
        st = user_status.get(cat.id, None)
        category_cards.append({
            'category': cat,
            'status': st,
        })

    return render(request, 'users/quiz_catalog.html', {'category_cards': category_cards})


@login_required
def take_quiz(request, category_id):
    """Interactive quiz testing domain skill knowledge."""
    category = get_object_or_404(QuizCategory, id=category_id)
    questions = list(category.questions.all())

    if not questions:
        messages.info(request, f'No questions available yet for {category.name}.')
        return redirect('users:quiz_catalog')

    if request.method == 'POST':
        total = len(questions)
        correct_count = 0
        answers_to_save = []

        for q in questions:
            chosen = request.POST.get(f'question_{q.id}', '').strip()
            is_correct = (chosen == q.correct_answer.strip())
            if is_correct:
                correct_count += 1
            answers_to_save.append((q, chosen, is_correct))

        score_percentage = int(round((correct_count / total) * 100)) if total > 0 else 0
        passed = score_percentage >= category.passing_score

        # Save Attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            category=category,
            score_percentage=score_percentage,
            total_questions=total,
            correct_count=correct_count,
            passed=passed,
        )

        for q, chosen, is_correct in answers_to_save:
            UserAnswer.objects.create(
                attempt=attempt,
                user=request.user,
                question=q,
                selected_answer=chosen,
                is_correct=is_correct,
            )

        # If passed, verify and update candidate's Skill record
        if passed:
            skill_obj, created = Skill.objects.get_or_create(
                user=request.user,
                name=category.name,
                defaults={
                    'level': score_percentage,
                    'is_verified': True,
                    'verified_at': timezone.now(),
                }
            )
            if not created:
                skill_obj.level = max(skill_obj.level, score_percentage)
                skill_obj.is_verified = True
                skill_obj.verified_at = timezone.now()
                skill_obj.save()

            request.user.is_verified = True
            request.user.save(update_fields=['is_verified'])

            messages.success(
                request,
                f'Congratulations! You passed the {category.name} assessment with {score_percentage}%. '
                f'Verified badge unlocked!'
            )
        else:
            messages.warning(
                request,
                f'You scored {score_percentage}%. The passing threshold is {category.passing_score}%. '
                'Review the solutions below and try again!'
            )

        return redirect('users:quiz_result', attempt_id=attempt.id)

    return render(request, 'users/take_quiz.html', {
        'category': category,
        'questions': questions,
    })


@login_required
def quiz_result(request, attempt_id):
    """Displays detailed breakdown of a completed quiz attempt."""
    attempt = get_object_or_404(QuizAttempt.objects.select_related('category'), id=attempt_id, user=request.user)
    user_answers = attempt.answers.select_related('question').all()

    return render(request, 'users/quiz_result.html', {
        'attempt': attempt,
        'user_answers': user_answers,
    })


@login_required
def my_applications(request):
    """View all job applications submitted by candidate."""
    if request.user.user_type != 'seeker':
        return redirect('jobs:home')

    applications = request.user.applications.select_related('job', 'job__company').order_by('-applied_date')
    return render(request, 'users/my_applications.html', {'applications': applications})
