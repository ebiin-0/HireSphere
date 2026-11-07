from django.shortcuts import render
from .models import Profile, Skill, Question, UserAnswer
import PyPDF2

def analyze_resume(file):
    text = ""
    try:
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content
    except Exception as e:
        print(e)
        return 0, []

    keywords = ["python","java","django","html","css","sql"]
    score = 0
    found = []

    for k in keywords:
        if k in text.lower():
            score += 10
            found.append(k)

    return score, found

def profile(request):
    profile = request.user.profile
    score = 0
    skills_found = []

    if profile.resume:
        with open(profile.resume.path, 'rb') as f:
            score, skills_found = analyze_resume(f)

        for s in skills_found:
            Skill.objects.get_or_create(user=request.user, name=s, defaults={"level":50})

    skills = Skill.objects.filter(user=request.user)

    return render(request,"users/profile.html",{"score":score,"skills":skills})

def quiz(request):
    questions = Question.objects.all()

    if request.method == "POST":
        score = 0
        for q in questions:
            ans = request.POST.get(str(q.id))
            if ans == q.correct_answer:
                score += 1

            UserAnswer.objects.create(user=request.user,question=q,selected_answer=ans)

        return render(request,"users/quiz_result.html",{"score":score})

    return render(request,"users/quiz.html",{"questions":questions})
