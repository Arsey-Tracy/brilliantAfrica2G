"""
Auto-generated migration for new models.
"""

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ussd', '0001_initial'),
    ]

    operations = [
        # Add fields to Student
        migrations.AddField(
            model_name='student',
            name='subscription_tier',
            field=models.CharField(
                choices=[('free', 'Free'), ('basic', 'Basic ($5/month)'), 
                         ('premium', 'Premium ($10/month)'), ('school', 'School ($20/month)')],
                default='free', max_length=20
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='subscription_start',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='subscription_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='preferred_language',
            field=models.CharField(
                choices=[('en', 'English'), ('sw', 'Swahili'), ('yo', 'Yoruba'),
                        ('ha', 'Hausa'), ('am', 'Amharic'), ('fr', 'French')],
                default='en', max_length=5
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='curriculum_standard',
            field=models.CharField(
                choices=[('waec', 'WAEC (West Africa)'), ('neco', 'NECO (Nigeria)'),
                        ('kcse', 'KCSE (Kenya)'), ('ethiopian', 'Ethiopian Curriculum'),
                        ('cambridge', 'Cambridge International'), ('custom', 'Custom')],
                default='waec', max_length=20
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='school_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='grade_level',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='last_activity',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Add fields to Teacher
        migrations.AddField(
            model_name='teacher',
            name='subject_specialization',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='teacher',
            name='school_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='certification_level',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='teacher',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='teacher',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='supported_curricula',
            field=models.CharField(default='waec', help_text='Comma-separated curriculum standards',
                                 max_length=200),
        ),
        migrations.AddField(
            model_name='teacher',
            name='supported_languages',
            field=models.CharField(default='en', help_text='Comma-separated language codes',
                                 max_length=50),
        ),
        
        # Add fields to Parent
        migrations.AddField(
            model_name='parent',
            name='email',
            field=models.EmailField(blank=True, null=True, max_length=254),
        ),
        migrations.AddField(
            model_name='parent',
            name='receive_progress_reports',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='parent',
            name='report_frequency',
            field=models.CharField(
                choices=[('weekly', 'Weekly'), ('bi-weekly', 'Bi-weekly'), ('monthly', 'Monthly')],
                default='weekly', max_length=20
            ),
        ),
        migrations.AddField(
            model_name='parent',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddManyToManyField(
            model_name='parent',
            name='students',
            to='ussd.student',
            related_name='parents',
        ),
        
        # Create Payment model
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('subscription_tier', models.CharField(
                    choices=[('free', 'Free'), ('basic', 'Basic ($5/month)'),
                            ('premium', 'Premium ($10/month)'), ('school', 'School ($20/month)')],
                    max_length=20)),
                ('payment_method', models.CharField(
                    choices=[('mpesa', 'M-Pesa (Kenya)'), ('mtn', 'MTN Money (Uganda, Ghana)'),
                            ('airtel', 'Airtel Money'), ('flutterwave', 'Flutterwave'),
                            ('stripe', 'Stripe'), ('paypal', 'PayPal')],
                    max_length=20)),
                ('transaction_id', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('completed', 'Completed'),
                            ('failed', 'Failed'), ('refunded', 'Refunded')],
                    default='pending', max_length=20)),
                ('phone_number_used', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='payments', to='ussd.student')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # Create Subscription model
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('tier', models.CharField(
                    choices=[('free', 'Free'), ('basic', 'Basic ($5/month)'),
                            ('premium', 'Premium ($10/month)'), ('school', 'School ($20/month)')],
                    default='free', max_length=20)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('auto_renew', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_payment', models.ForeignKey(blank=True, null=True,
                                                  on_delete=django.db.models.deletion.SET_NULL,
                                                  to='ussd.payment')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='current_subscription', to='ussd.student')),
            ],
        ),
        
        # Create Subject model
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('curricula', models.CharField(default='waec', help_text='Comma-separated curriculum codes',
                                             max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Create Topic model
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('difficulty_level', models.IntegerField(default=1)),
                ('keywords', models.TextField(help_text='Comma-separated keywords for AI matching')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='topics', to='ussd.subject')),
            ],
            options={
                'ordering': ['subject', 'difficulty_level', 'name'],
            },
        ),
        
        # Create CurriculumGuide model
        migrations.CreateModel(
            name='CurriculumGuide',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('curriculum_standard', models.CharField(
                    choices=[('waec', 'WAEC (West Africa)'), ('neco', 'NECO (Nigeria)'),
                            ('kcse', 'KCSE (Kenya)'), ('ethiopian', 'Ethiopian Curriculum'),
                            ('cambridge', 'Cambridge International'), ('custom', 'Custom')],
                    max_length=20)),
                ('language', models.CharField(
                    choices=[('en', 'English'), ('sw', 'Swahili'), ('yo', 'Yoruba'),
                            ('ha', 'Hausa'), ('am', 'Amharic'), ('fr', 'French')],
                    default='en', max_length=5)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                               related_name='curriculum_guides', to='ussd.teacher')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                          related_name='guides', to='ussd.topic')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # Create Quiz model
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('difficulty_level', models.IntegerField(default=1)),
                ('total_questions', models.IntegerField(default=10)),
                ('passing_score', models.IntegerField(default=70)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True,
                                               on_delete=django.db.models.deletion.SET_NULL,
                                               to='ussd.teacher')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                          related_name='quizzes', to='ussd.topic')),
            ],
        ),
        
        # Create QuizAttempt model
        migrations.CreateModel(
            name='QuizAttempt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('score', models.IntegerField()),
                ('passed', models.BooleanField()),
                ('time_taken_seconds', models.IntegerField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                         related_name='attempts', to='ussd.quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='quiz_attempts', to='ussd.student')),
            ],
            options={
                'ordering': ['-completed_at'],
            },
        ),
        
        # Create StudentProgress model
        migrations.CreateModel(
            name='StudentProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('total_questions_asked', models.IntegerField(default=0)),
                ('total_quizzes_taken', models.IntegerField(default=0)),
                ('total_quizzes_passed', models.IntegerField(default=0)),
                ('subjects_studied', models.IntegerField(default=0)),
                ('topics_completed', models.IntegerField(default=0)),
                ('average_quiz_score', models.FloatField(default=0.0)),
                ('overall_grade', models.CharField(default='N/A', max_length=5)),
                ('last_study_date', models.DateField(blank=True, null=True)),
                ('last_quiz_date', models.DateField(blank=True, null=True)),
                ('streak_days', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='progress', to='ussd.student')),
            ],
        ),
        
        # Create AssignmentSubmission model
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('due_date', models.DateTimeField()),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('submission_text', models.TextField(blank=True)),
                ('grade', models.IntegerField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('graded_by', models.ForeignKey(blank=True, null=True,
                                              on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='graded_submissions', to='ussd.teacher')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='submissions', to='ussd.student')),
            ],
            options={
                'ordering': ['-due_date'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['student', 'status'], name='ussd_paymen_student_status_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['transaction_id'], name='ussd_paymen_transac_idx'),
        ),
        migrations.AddIndex(
            model_name='subject',
            index=models.Index(fields=['name'], name='ussd_subject_name_idx'),
        ),
        migrations.AddIndex(
            model_name='topic',
            index=models.Index(fields=['subject', 'difficulty_level'], name='ussd_topic_subject_level_idx'),
        ),
        migrations.AddIndex(
            model_name='curriculumguide',
            index=models.Index(fields=['topic', 'curriculum_standard'], name='ussd_guide_topic_curric_idx'),
        ),
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(fields=['student', 'quiz'], name='ussd_attempt_student_quiz_idx'),
        ),
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(fields=['student', 'passed'], name='ussd_attempt_student_passed_idx'),
        ),
        migrations.AddIndex(
            model_name='assignmentsubmission',
            index=models.Index(fields=['student', 'due_date'], name='ussd_assign_student_due_idx'),
        ),
    ]
