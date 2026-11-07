from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('analyze-resume/', views.analyze_resume_now, name='analyze_resume'),
    path('quizzes/', views.quiz_catalog, name='quiz_catalog'),
    path('quizzes/<int:category_id>/take/', views.take_quiz, name='take_quiz'),
    path('quizzes/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
