from django.urls import path
from .views import ussd_callback, sms_reply_handler
from .api_views import (
    waitlist_join, teacher_register, payment_initiate, payment_verify,
    student_progress, quiz_submit, get_quizzes, get_curriculum_guides,
    teacher_create_quiz, assignment_submit, teacher_grade_assignment,
    school_dashboard
)

urlpatterns = [
    # USSD and SMS
    path('ussd/', ussd_callback, name='ussd_callback'),
    path('sms/', sms_reply_handler, name='sms_reply_handler'),
    
    # API endpoints
    path('api/waitlist/join/', waitlist_join, name='waitlist_join'),
    path('api/teacher/register/', teacher_register, name='teacher_register'),
    path('api/payment/initiate/', payment_initiate, name='payment_initiate'),
    path('api/payment/verify/', payment_verify, name='payment_verify'),
    path('api/student/progress/', student_progress, name='student_progress'),
    path('api/quiz/submit/', quiz_submit, name='quiz_submit'),
    path('api/quizzes/', get_quizzes, name='get_quizzes'),
    path('api/guides/', get_curriculum_guides, name='get_curriculum_guides'),
    path('api/teacher/quiz/create/', teacher_create_quiz, name='teacher_create_quiz'),
    path('api/assignment/submit/', assignment_submit, name='assignment_submit'),
    path('api/teacher/grade/', teacher_grade_assignment, name='teacher_grade_assignment'),
    path('api/school/dashboard/', school_dashboard, name='school_dashboard'),
]
