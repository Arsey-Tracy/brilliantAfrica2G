from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Student, Teacher, Parent, SchoolAdmin, Role,
    Payment, Subscription,
    Subject, Topic, CurriculumGuide, Quiz, QuizAttempt, StudentProgress, AssignmentSubmission
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'subscription_status', 
                    'preferred_language', 'curriculum_standard', 'grade_level', 'enrollment_date')
    list_filter = ('subscription_tier', 'curriculum_standard', 'preferred_language', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name', 'school_name')
    readonly_fields = ('enrollment_date', 'created_at', 'updated_at', 'last_activity')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'first_name', 'last_name', 'other_name', 'phone_number')
        }),
        ('Education', {
            'fields': ('school_name', 'grade_level', 'curriculum_standard', 'preferred_language')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'subscription_start', 'subscription_end', 'is_active')
        }),
        ('Activity', {
            'fields': ('enrollment_date', 'last_activity', 'created_at', 'updated_at')
        }),
    )
    
    def subscription_status(self, obj):
        status = "✓ Active" if obj.is_subscription_active() else "✗ Inactive"
        return format_html(f'<span style="color: green;">{status}</span>' if obj.is_subscription_active() 
                          else f'<span style="color: red;">{status}</span>')
    subscription_status.short_description = 'Status'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('verification_badge', 'phone_number', 'first_name', 'last_name', 
                    'subject_specialization', 'school_name', 'supported_curricula', 'is_active')
    list_filter = ('is_verified', 'is_active', 'supported_curricula')
    search_fields = ('phone_number', 'first_name', 'last_name', 'subject_specialization', 'school_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'first_name', 'last_name', 'middle_name', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('subject_specialization', 'school_name', 'certification_level')
        }),
        ('Verification & Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Curriculum & Language', {
            'fields': ('supported_curricula', 'supported_languages')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green; font-weight: bold;">✓ VERIFIED</span>')
        return format_html('<span style="color: orange;">○ PENDING</span>')
    verification_badge.short_description = 'Verification'


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'email', 'receive_progress_reports', 'is_active')
    list_filter = ('receive_progress_reports', 'report_frequency', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('students',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'first_name', 'last_name', 'middle_name', 'phone_number', 'email')
        }),
        ('Linked Students', {
            'fields': ('students',)
        }),
        ('Notification Settings', {
            'fields': ('receive_progress_reports', 'report_frequency')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(SchoolAdmin)
class SchoolAdminAdmin(admin.ModelAdmin):
    list_display = ('verification_badge', 'school_name', 'school_code', 'country', 
                    'first_name', 'last_name', 'is_active')
    list_filter = ('is_verified', 'is_active', 'country')
    search_fields = ('school_name', 'school_code', 'phone_number', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('School Information', {
            'fields': ('id', 'school_name', 'school_code', 'country')
        }),
        ('Contact Person', {
            'fields': ('first_name', 'last_name', 'phone_number', 'email')
        }),
        ('Verification & Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green; font-weight: bold;">✓ VERIFIED</span>')
        return format_html('<span style="color: orange;">○ PENDING</span>')
    verification_badge.short_description = 'Verification'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'role')
    list_filter = ('role',)
    search_fields = ('phone_number',)


# ========== PAYMENT & SUBSCRIPTION MODELS ==========

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'student', 'amount', 'currency', 'payment_method', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method', 'subscription_tier', 'created_at')
    search_fields = ('transaction_id', 'student__phone_number', 'phone_number_used')
    readonly_fields = ('id', 'created_at', 'completed_at', 'transaction_id')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'student', 'transaction_id', 'payment_method')
        }),
        ('Amount & Subscription', {
            'fields': ('amount', 'currency', 'subscription_tier')
        }),
        ('Payment Details', {
            'fields': ('phone_number_used', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'completed': 'green',
            'pending': 'orange',
            'failed': 'red',
            'refunded': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'tier', 'start_date', 'end_date', 'auto_renew', 'is_active_badge')
    list_filter = ('tier', 'auto_renew', 'is_active')
    search_fields = ('student__phone_number', 'student__first_name', 'student__last_name')
    readonly_fields = ('id', 'start_date', 'created_at', 'updated_at')
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Active'


# ========== CURRICULUM MODELS ==========

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'curricula', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'difficulty_level', 'is_active')
    list_filter = ('subject', 'difficulty_level', 'is_active')
    search_fields = ('name', 'keywords')
    readonly_fields = ('created_at',)


@admin.register(CurriculumGuide)
class CurriculumGuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'curriculum_standard', 'language', 'created_by', 'verification_badge')
    list_filter = ('curriculum_standard', 'language', 'is_verified')
    search_fields = ('title', 'topic__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    
    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: orange;">○ Pending</span>')
    verification_badge.short_description = 'Verified'


# ========== GRADING & PERFORMANCE MODELS ==========

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty_level', 'total_questions', 'passing_score', 'created_by')
    list_filter = ('difficulty_level', 'is_verified')
    search_fields = ('title', 'topic__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'passed_badge', 'completed_at')
    list_filter = ('passed', 'completed_at')
    search_fields = ('student__phone_number', 'quiz__title')
    readonly_fields = ('completed_at',)
    date_hierarchy = 'completed_at'
    
    def passed_badge(self, obj):
        if obj.passed:
            return format_html('<span style="color: green; font-weight: bold;">✓ PASS</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ FAIL</span>')
    passed_badge.short_description = 'Result'


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'overall_grade', 'total_quizzes_passed', 'average_quiz_score', 
                    'streak_days', 'last_study_date')
    list_filter = ('overall_grade',)
    search_fields = ('student__phone_number', 'student__first_name')
    readonly_fields = ('student', 'updated_at')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'due_date', 'submitted_at', 'grade', 'graded_by')
    list_filter = ('due_date', 'graded_by')
    search_fields = ('title', 'student__phone_number')
    readonly_fields = ('created_at', 'submitted_at', 'graded_at')
    date_hierarchy = 'due_date'