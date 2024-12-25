# Generated by Django 5.1.4 on 2024-12-24 11:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('department_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('location', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('book_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('book_name', models.CharField(max_length=255)),
                ('book_description', models.TextField(null=True)),
                ('category', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('book_cover', models.ImageField(blank=True, null=True, upload_to='book_covers/')),
                ('status', models.CharField(choices=[('AVAILABLE', 'Available'), ('BORROWED', 'Borrowed')], default='AVAILABLE', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('assignment_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('due_date', models.DateField()),
                ('file', models.FileField(blank=True, null=True, upload_to='assignments/instructions/')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='main_app.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseMaterial',
            fields=[
                ('material_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='course_materials/')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='main_app.course')),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('enrollment_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('enrollment_date', models.DateField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='main_app.course')),
            ],
        ),
        migrations.CreateModel(
            name='BookLending',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrow_date', models.DateTimeField(auto_now_add=True)),
                ('return_date', models.DateTimeField(blank=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.library')),
            ],
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('student_id', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('address', models.TextField()),
                ('professor_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('specialization', models.CharField(max_length=100)),
                ('courses', models.ManyToManyField(blank=True, related_name='professors', to='main_app.course')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='professors', to='main_app.department')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('room_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('room_type', models.CharField(max_length=100)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='main_app.department')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('schedule_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('type', models.CharField(max_length=50)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='main_app.course')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedules', to='main_app.room')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('student_id', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('address', models.TextField()),
                ('staff_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('position', models.CharField(max_length=100)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff', to='main_app.department')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('address', models.TextField()),
                ('student_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('enrolled_courses', models.ManyToManyField(related_name='students', through='main_app.Enrollment', to='main_app.course')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='library',
            name='borrowers',
            field=models.ManyToManyField(related_name='borrowed_books', through='main_app.BookLending', to='main_app.student'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='main_app.student'),
        ),
        migrations.AddField(
            model_name='booklending',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.student'),
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('submission_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('file', models.FileField(upload_to='assignments/')),
                ('grade', models.CharField(blank=True, default='Not Graded', max_length=5, null=True)),
                ('submission_date', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='main_app.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='main_app.student')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='booklending',
            unique_together={('book', 'student', 'borrow_date')},
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('attendance_id', models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True)),
                ('is_present', models.BooleanField(default=False)),
                ('attendance_percent', models.FloatField(default=0)),
                ('date_marked', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='main_app.course')),
                ('schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='main_app.schedule')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='main_app.student')),
            ],
            options={
                'unique_together': {('student', 'course', 'schedule')},
            },
        ),
    ]
