import uuid
from django.db import models
from django.utils import timezone

# Language choices for multi-language support
LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('sw', 'Swahili'),
    ('yo', 'Yoruba'),
    ('ha', 'Hausa'),
    ('am', 'Amharic'),
    ('fr', 'French'),
]

# Subscription tier choices
SUBSCRIPTION_CHOICES = [
    ('free', 'Free'),
    ('basic', 'Basic ($5/month)'),
    ('premium', 'Premium ($10/month)'),
    ('school', 'School ($20/month)'),
]

# Curriculum standards
CURRICULUM_CHOICES = [
    ('waec', 'WAEC (West Africa)'),
    ('neco', 'NECO (Nigeria)'),
    ('kcse', 'KCSE (Kenya)'),
    ('ethiopian', 'Ethiopian Curriculum'),
    ('cambridge', 'Cambridge International'),
    ('custom', 'Custom'),
]

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    other_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    enrollment_date = models.DateField(auto_now_add=True)
    
    # Subscription and payment
    subscription_tier = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    
    # Language and curriculum preferences
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    curriculum_standard = models.CharField(max_length=20, choices=CURRICULUM_CHOICES, default='waec')
    
    # Profile
    school_name = models.CharField(max_length=255, blank=True, null=True)
    grade_level = models.IntegerField(null=True, blank=True)  # 1-12 or equivalent
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['phone_number'])]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"
    
    def is_subscription_active(self):
        if self.subscription_tier == 'free':
            return True
        if self.subscription_end:
            return timezone.now().date() <= self.subscription_end
        return False


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    
    # Professional info
    subject_specialization = models.CharField(max_length=100, blank=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    certification_level = models.CharField(max_length=50, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)  # Verified teachers get higher weight in hybrid AI
    is_active = models.BooleanField(default=True)
    
    # Curriculum support
    supported_curricula = models.CharField(
        max_length=200, 
        default='waec',
        help_text="Comma-separated curriculum standards they support"
    )
    supported_languages = models.CharField(
        max_length=50,
        default='en',
        help_text="Comma-separated language codes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_verified', '-created_at']
        indexes = [models.Index(fields=['phone_number'])]

    def __str__(self):
        verified = "✓" if self.is_verified else "○"
        return f"{verified} {self.first_name} {self.last_name} ({self.subject_specialization})"


class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    
    # Linked students
    students = models.ManyToManyField(Student, related_name='parents', blank=True)
    
    # Notification preferences
    receive_progress_reports = models.BooleanField(default=True)
    report_frequency = models.CharField(
        max_length=20,
        choices=[('weekly', 'Weekly'), ('bi-weekly', 'Bi-weekly'), ('monthly', 'Monthly')],
        default='weekly'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['phone_number'])]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

class SchoolAdmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    
    # School info
    school_name = models.CharField(max_length=255)
    school_code = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=100)
    
    # Permissions
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_verified', '-created_at']
        indexes = [models.Index(fields=['school_code'])]

    def __str__(self):
        return f"{self.school_name} - {self.first_name} {self.last_name}"

class Role(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('admin', 'School Admin'),
    ]
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def __str__(self):
        return f"{self.phone_number} - {self.get_role_display()}"


# ========== PAYMENT & SUBSCRIPTION MODELS ==========

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa (Kenya)'),
        ('mtn', 'MTN Money (Uganda, Ghana)'),
        ('airtel', 'Airtel Money'),
        ('flutterwave', 'Flutterwave'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    subscription_tier = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Local payment references (for M-Pesa, MTN, etc.)
    phone_number_used = models.CharField(max_length=15)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.student.phone_number} - {self.subscription_tier} - {self.status}"


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='current_subscription')
    
    tier = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    
    # Used for renewing subscriptions
    last_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.phone_number} - {self.tier}"
    
    def is_expired(self):
        if self.tier == 'free':
            return False
        return self.end_date and timezone.now().date() > self.end_date


# ========== CURRICULUM & CONTENT MODELS ==========

class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Which curricula this subject belongs to
    curricula = models.CharField(
        max_length=200,
        default='waec',
        help_text="Comma-separated curriculum codes"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Difficulty level for adaptive learning
    difficulty_level = models.IntegerField(default=1, choices=[(i, f"Level {i}") for i in range(1, 6)])
    
    # Keywords for AI matching
    keywords = models.TextField(help_text="Comma-separated keywords for better AI matching")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject', 'difficulty_level', 'name']
        indexes = [models.Index(fields=['subject', 'difficulty_level'])]

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class CurriculumGuide(models.Model):
    """Curated study guides aligned with curriculum standards"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='guides')
    
    title = models.CharField(max_length=255)
    content = models.TextField()  # Structured guide content
    curriculum_standard = models.CharField(max_length=20, choices=CURRICULUM_CHOICES)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    
    # Who created it
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='curriculum_guides')
    is_verified = models.BooleanField(default=False)  # Admin verified content
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['topic', 'curriculum_standard'])]

    def __str__(self):
        return f"{self.topic.name} - {self.language}"


# ========== GRADING & PERFORMANCE MODELS ==========

class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='quizzes')
    
    title = models.CharField(max_length=255)
    difficulty_level = models.IntegerField(default=1, choices=[(i, f"Level {i}") for i in range(1, 6)])
    total_questions = models.IntegerField(default=10)
    passing_score = models.IntegerField(default=70)  # Percentage
    
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.name} - {self.title}"


class QuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    score = models.IntegerField()  # Out of 100
    passed = models.BooleanField()
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['student', 'quiz']),
            models.Index(fields=['student', 'passed']),
        ]

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"{self.student.phone_number} - {self.quiz.title} - {self.score}% [{status}]"


class StudentProgress(models.Model):
    """Aggregate progress tracking for each student"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='progress')
    
    total_questions_asked = models.IntegerField(default=0)
    total_quizzes_taken = models.IntegerField(default=0)
    total_quizzes_passed = models.IntegerField(default=0)
    
    # By subject tracking
    subjects_studied = models.IntegerField(default=0)
    topics_completed = models.IntegerField(default=0)
    
    # Performance metrics
    average_quiz_score = models.FloatField(default=0.0)
    overall_grade = models.CharField(max_length=5, default='N/A')  # A, B, C, D, F
    
    last_study_date = models.DateField(null=True, blank=True)
    last_quiz_date = models.DateField(null=True, blank=True)
    
    streak_days = models.IntegerField(default=0)  # Consecutive days of activity
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.phone_number} - Grade {self.overall_grade}"
    
    def calculate_overall_grade(self):
        """Calculate grade from quiz performance"""
        if self.total_quizzes_taken == 0:
            return 'N/A'
        
        percentage = self.average_quiz_score
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'


class AssignmentSubmission(models.Model):
    """For schools to assign homework/projects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    submission_text = models.TextField(blank=True)
    
    grade = models.IntegerField(null=True, blank=True)  # Out of 100
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']
        indexes = [models.Index(fields=['student', 'due_date'])]

    def __str__(self):
        return f"{self.student.phone_number} - {self.title}"