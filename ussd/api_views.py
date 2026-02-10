"""
API views for BrilliantAfrica
Handles: Teacher registration, Student assessments, Payments, Progress tracking
"""

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q
from django.utils import timezone
import json
import logging

from ussd.models import (
    Student, Teacher, Parent, SchoolAdmin, Role, Payment, Subscription,
    Subject, Topic, Quiz, QuizAttempt, StudentProgress, AssignmentSubmission, CurriculumGuide
)
from ussd.services.payment_service import PaymentProcessor, SubscriptionManager
from ussd.services.language_service import LanguageService
from ussd.services.curriculum_service import CurriculumAlignmentService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def waitlist_join(request):
    """Add user to waitlist"""
    try:
        data = json.loads(request.body)
        
        first_name = data.get('first_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        email = data.get('email', '').strip()
        country = data.get('country', '').strip()

        # Validate
        if not all([first_name, phone_number, email]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields'
            }, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid email address'
            }, status=400)

        # Check if already exists
        if Student.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({
                'success': False,
                'message': 'Phone number already registered'
            }, status=400)

        # Create student
        student = Student.objects.create(
            first_name=first_name,
            phone_number=phone_number,
            subscription_tier='free',
        )

        # Create initial progress
        StudentProgress.objects.create(student=student)

        # Send welcome SMS
        from ussd.services.sms_service import SMSService
        msg = f"Welcome to BrilliantAfrica, {first_name}! Dial *483*3268# to start learning with your AI tutor."
        SMSService.send_sms(phone_number, msg)

        logger.info(f"New waitlist signup: {phone_number}")

        return JsonResponse({
            'success': True,
            'message': 'Successfully joined the waitlist!',
            'student_id': str(student.id)
        })

    except Exception as e:
        logger.error(f"Waitlist error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def teacher_register(request):
    """Register as a teacher"""
    try:
        data = json.loads(request.body)

        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        subject = data.get('subject_specialization', '').strip()
        school = data.get('school_name', '').strip()
        certification = data.get('certification_level', '').strip()

        if not all([first_name, last_name, phone_number, subject]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields'
            }, status=400)

        # Check if teacher exists
        if Teacher.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({
                'success': False,
                'message': 'Phone number already registered'
            }, status=400)

        # Create teacher
        teacher = Teacher.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            subject_specialization=subject,
            school_name=school,
            certification_level=certification,
            is_active=True,
        )

        # Create role
        Role.objects.create(phone_number=phone_number, role='teacher')

        # Send confirmation
        msg = f"Welcome to BrilliantAfrica, {first_name}! Your teacher account has been created. Use *483*3268# to access the teacher portal."
        from ussd.services.sms_service import SMSService
        SMSService.send_sms(phone_number, msg)

        logger.info(f"New teacher registration: {phone_number} ({subject})")

        return JsonResponse({
            'success': True,
            'message': 'Teacher account created successfully!',
            'teacher_id': str(teacher.id)
        })

    except Exception as e:
        logger.error(f"Teacher registration error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Server error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def payment_initiate(request):
    """Initiate payment for subscription"""
    try:
        data = json.loads(request.body)

        phone_number = data.get('phone_number', '').strip()
        subscription_tier = data.get('subscription_tier', 'basic')
        payment_method = data.get('payment_method', 'flutterwave')

        # Get or create student
        student = Student.objects.filter(phone_number=phone_number).first()
        if not student:
            return JsonResponse({
                'success': False,
                'message': 'Student not found. Please register first.'
            }, status=404)

        # Initiate payment
        payment_id, message, method = PaymentProcessor.initiate_payment(
            student_id=student.id,
            subscription_tier=subscription_tier,
            phone_number=phone_number,
            language=student.preferred_language
        )

        if not payment_id:
            return JsonResponse({
                'success': False,
                'message': message
            }, status=400)

        return JsonResponse({
            'success': True,
            'message': message,
            'payment_id': payment_id,
            'payment_method': method
        })

    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Payment initiation failed'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def payment_verify(request):
    """Verify payment after completion"""
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        confirmation_code = data.get('confirmation_code')

        success, message = PaymentProcessor.verify_payment(payment_id, confirmation_code)

        return JsonResponse({
            'success': success,
            'message': message
        })

    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Verification failed'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def student_progress(request):
    """Get student progress"""
    phone_number = request.GET.get('phone_number')
    
    if not phone_number:
        return JsonResponse({'success': False, 'message': 'Phone number required'}, status=400)

    try:
        student = Student.objects.get(phone_number=phone_number)
        progress = StudentProgress.objects.get(student=student)

        return JsonResponse({
            'success': True,
            'data': {
                'student_name': f"{student.first_name} {student.last_name}",
                'grade_level': student.grade_level,
                'curriculum': student.curriculum_standard,
                'total_questions': progress.total_questions_asked,
                'quizzes_taken': progress.total_quizzes_taken,
                'quizzes_passed': progress.total_quizzes_passed,
                'average_score': progress.average_quiz_score,
                'overall_grade': progress.overall_grade,
                'last_activity': student.last_activity.isoformat() if student.last_activity else None,
            }
        })

    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student not found'}, status=404)
    except Exception as e:
        logger.error(f"Progress retrieval error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error fetching progress'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def quiz_submit(request):
    """Submit quiz answers"""
    try:
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        quiz_id = data.get('quiz_id')
        score = data.get('score')
        time_taken = data.get('time_taken_seconds')

        student = Student.objects.get(id=student_id)
        quiz = Quiz.objects.get(id=quiz_id)

        passed = score >= quiz.passing_score

        # Create attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=score,
            passed=passed,
            time_taken_seconds=time_taken
        )

        # Update progress
        progress = StudentProgress.objects.get(student=student)
        progress.total_quizzes_taken += 1
        if passed:
            progress.total_quizzes_passed += 1
        
        # Update average score
        all_attempts = QuizAttempt.objects.filter(student=student)
        progress.average_quiz_score = all_attempts.aggregate(Avg('score'))['score__avg'] or 0
        progress.overall_grade = progress.calculate_overall_grade()
        progress.last_quiz_date = timezone.now().date()
        progress.save()

        return JsonResponse({
            'success': True,
            'message': f"Quiz submitted! Score: {score}%",
            'passed': passed,
            'data': {
                'score': score,
                'passing_score': quiz.passing_score,
                'average_score': progress.average_quiz_score,
            }
        })

    except (Student.DoesNotExist, Quiz.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid student or quiz'}, status=404)
    except Exception as e:
        logger.error(f"Quiz submission error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error submitting quiz'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_quizzes(request):
    """Get quizzes for a subject"""
    subject_id = request.GET.get('subject_id')
    difficulty = request.GET.get('difficulty')

    try:
        quizzes = Quiz.objects.filter(topic__subject_id=subject_id, is_verified=True)
        
        if difficulty:
            quizzes = quizzes.filter(difficulty_level=int(difficulty))

        data = [{
            'id': str(q.id),
            'title': q.title,
            'total_questions': q.total_questions,
            'difficulty': q.difficulty_level,
            'passing_score': q.passing_score,
        } for q in quizzes]

        return JsonResponse({
            'success': True,
            'quizzes': data
        })

    except Exception as e:
        logger.error(f"Get quizzes error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error fetching quizzes'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_curriculum_guides(request):
    """Get curriculum guides for a topic"""
    topic_id = request.GET.get('topic_id')
    language = request.GET.get('language', 'en')
    curriculum = request.GET.get('curriculum')

    try:
        guides = CurriculumGuide.objects.filter(
            topic_id=topic_id,
            language=language,
            is_verified=True
        )

        if curriculum:
            guides = guides.filter(curriculum_standard=curriculum)

        data = [{
            'id': str(g.id),
            'title': g.title,
            'content': g.content[:500],  # First 500 chars
            'curriculum': g.curriculum_standard,
            'language': g.language,
        } for g in guides]

        return JsonResponse({
            'success': True,
            'guides': data
        })

    except Exception as e:
        logger.error(f"Get guides error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error fetching guides'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def teacher_create_quiz(request):
    """Teacher creates a quiz"""
    try:
        data = json.loads(request.body)
        
        teacher_id = data.get('teacher_id')
        topic_id = data.get('topic_id')
        title = data.get('title')
        questions = data.get('questions', [])

        teacher = Teacher.objects.get(id=teacher_id)
        topic = Topic.objects.get(id=topic_id)

        quiz = Quiz.objects.create(
            topic=topic,
            title=title,
            total_questions=len(questions),
            created_by=teacher,
            difficulty_level=data.get('difficulty_level', 1),
            passing_score=data.get('passing_score', 70),
        )

        return JsonResponse({
            'success': True,
            'message': 'Quiz created successfully!',
            'quiz_id': str(quiz.id)
        })

    except (Teacher.DoesNotExist, Topic.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid teacher or topic'}, status=404)
    except Exception as e:
        logger.error(f"Quiz creation error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error creating quiz'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def assignment_submit(request):
    """Student submits assignment"""
    try:
        data = json.loads(request.body)
        
        student_id = data.get('student_id')
        assignment_id = data.get('assignment_id')
        submission_text = data.get('submission_text')

        student = Student.objects.get(id=student_id)
        assignment = AssignmentSubmission.objects.get(id=assignment_id, student=student)

        assignment.submitted_at = timezone.now()
        assignment.submission_text = submission_text
        assignment.save()

        return JsonResponse({
            'success': True,
            'message': 'Assignment submitted successfully!'
        })

    except (Student.DoesNotExist, AssignmentSubmission.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid student or assignment'}, status=404)
    except Exception as e:
        logger.error(f"Assignment submission error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error submitting assignment'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def teacher_grade_assignment(request):
    """Teacher grades an assignment"""
    try:
        data = json.loads(request.body)
        
        teacher_id = data.get('teacher_id')
        assignment_id = data.get('assignment_id')
        grade = data.get('grade')
        feedback = data.get('feedback', '')

        teacher = Teacher.objects.get(id=teacher_id)
        assignment = AssignmentSubmission.objects.get(id=assignment_id)

        assignment.grade = grade
        assignment.feedback = feedback
        assignment.graded_by = teacher
        assignment.graded_at = timezone.now()
        assignment.save()

        # Notify student
        student = assignment.student
        msg = f"Your assignment '{assignment.title}' has been graded: {grade}/100"
        from ussd.services.sms_service import SMSService
        SMSService.send_sms(student.phone_number, msg)

        return JsonResponse({
            'success': True,
            'message': 'Assignment graded successfully!'
        })

    except (Teacher.DoesNotExist, AssignmentSubmission.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid teacher or assignment'}, status=404)
    except Exception as e:
        logger.error(f"Grading error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error grading assignment'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def school_dashboard(request):
    """Get school admin dashboard data"""
    school_code = request.GET.get('school_code')

    try:
        admin = SchoolAdmin.objects.get(school_code=school_code)
        
        # Get all students in school
        students = Student.objects.filter(school_name=admin.school_name)
        
        total_students = students.count()
        active_subscriptions = Subscription.objects.filter(
            student__school_name=admin.school_name,
            is_active=True,
            tier__in=['premium', 'school']
        ).count()

        avg_score = QuizAttempt.objects.filter(
            student__school_name=admin.school_name
        ).aggregate(Avg('score'))['score__avg'] or 0

        return JsonResponse({
            'success': True,
            'data': {
                'school_name': admin.school_name,
                'total_students': total_students,
                'active_subscriptions': active_subscriptions,
                'average_score': round(avg_score, 2),
                'revenue_per_student': total_students > 0 and (active_subscriptions * 20) / total_students or 0,
            }
        })

    except SchoolAdmin.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'School not found'}, status=404)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error fetching dashboard'}, status=500)
