from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError

# Base abstract model
def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

class Person(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, validators=[validate_password])
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        abstract = True

# Models
class Student(Person):
    student_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    enrolled_courses = models.ManyToManyField("Course", through='Enrollment', related_name='students')

    def get_enrolled_courses(self):
        return self.enrolled_courses.all()

    def __str__(self):
        return self.name
    
class Professor(Person):
    professor_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="professors")
    courses = models.ManyToManyField('Course', related_name="professors", blank=True)
    specialization = models.CharField(max_length=100)

class BookLending(models.Model):
    book = models.ForeignKey('Library', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['book', 'student', 'borrow_date']

class Library(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BORROWED', 'Borrowed'),
    ]

    CATEGORY_CHOICES = [
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('SCIENCE', 'Science'),
        ('HISTORY', 'History'),
        ('MATH', 'Mathematics'),
        ('BIOLOGY', 'Biology'),
        ('PHYSICS', 'Physics'),
        ('CHEMISTRY', 'Chemistry'),
        ('ENGINEERING', 'Engineering'),
        ('MEDICINE', 'Medicine'),
        ('BUSINESS', 'Business'),
        ('LITERATURE', 'Literature'),
        ('PHILOSOPHY', 'Philosophy'),
        ('PSYCHOLOGY', 'Psychology'),
        ('SOCIOLOGY', 'Sociology'),
        ('POLITICAL_SCIENCE', 'Political Science'),
        ('ECONOMICS', 'Economics'),
        ('ART', 'Art'),
        ('MUSIC', 'Music'),
        ('SPORTS', 'Sports'),
        ('NOVEL', 'Novel'),
        ('SCIENCE_FICTION', 'Science Fiction'),
        ('THRILLER', 'Thriller'),
        ('PERSONAL_DEVELOPMENT', 'Personal Development'),
        ('COMPUTER_TECHNOLOGY', 'Computer Technology'),
        ('COMPUTER_SCIENCE', 'Computer Science'),
        ('OTHER', 'Other'),
    ]
    
    book_id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    book_name = models.CharField(max_length=255)
    book_description = models.TextField(null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='OTHER')
    quantity = models.PositiveIntegerField()
    book_cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AVAILABLE')
    borrowers = models.ManyToManyField(
        'Student',
        through=BookLending,
        related_name='borrowed_books'
    )

    def __str__(self):
        return self.book_name

class CourseMaterial(models.Model):
    material_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="materials")
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.name}"

class AssignmentSubmission(models.Model):
    submission_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="submitted_assignments")
    file = models.FileField(upload_to='assignments/')
    grade = models.CharField(max_length=5, null=True, blank=True, default="Not Graded")
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submission_date']
        
    def __str__(self):
        return f"{self.student.name}'s submission for {self.assignment.title}"

class Room(models.Model):
    room_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    room_type = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="rooms")

class Department(models.Model):
    department_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)

class Course(models.Model):
    course_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    CLASS_CHOICES = [
        ('ON_CAMPUS', 'On Campus'),
        ('ONLINE', 'Online'),
        ('LAB', 'Laboratory'),
        ('TUTORIAL', 'Tutorial')
    ]

    schedule_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    time = models.TimeField()
    type = models.CharField(max_length=50, choices=CLASS_CHOICES, default='ON_CAMPUS')
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, related_name="schedules")

    class Meta:
        ordering = ['date', 'time']  # Add ordering

    def __str__(self):
        return f"Schedule for {self.course.name} on {self.date} at {self.time}"

class Assignment(models.Model):
    assignment_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/instructions/', null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="assignments")

    def __str__(self):
        return f"{self.title} - {self.course.name}"

class Attendance(models.Model):
    attendance_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendances")
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="attendances", null=True, blank=True)
    is_present = models.BooleanField(default=False)
    attendance_percent = models.FloatField(default=0)
    date_marked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'course', 'schedule']

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.schedule.date if self.schedule else 'No Schedule'}"

class Enrollment(models.Model):
    enrollment_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        (1, "High"),
        (2, "Medium"),
        (3, "Low"),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    ordering = ['priority', '-created_at']  # Sort by priority (ascending) and then by creation date (descending)

def __str__(self):
    return f"{self.title} (Priority: {self.get_priority_display()})"




# Define the prefix mapping
prefix_mapping = {
    'Student': 'STU',
    'Professor': 'PRO',
    'Library': 'LIB',
    'Room': 'ROM',
    'Department': 'DEP',
    'Course': 'COU',
    'Schedule': 'SCH',
    'Assignment': 'ASS',
    'Attendance': 'ATT',
    'Enrollment': 'ENR',
    'CourseMaterial': 'MAT',
    'AssignmentSubmission': 'SUB',
}

# List of models with auto-generated IDs
models_with_auto_id = [
    Student, Professor, Library, Room, Department, Course,
    Schedule, Assignment, Attendance, Enrollment, CourseMaterial, AssignmentSubmission
]

# Helper function to register signals dynamically
def create_signal(model):
    @receiver(pre_save, sender=model)
    def generate_auto_id(sender, instance, **kwargs):
        if not instance.pk:  # Only generate ID for new objects
            prefix = prefix_mapping.get(sender.__name__)
            if prefix:
                # Dynamically resolve the primary key field name
                pk_field_name = instance._meta.pk.name
                max_id = sender.objects.count() + 1
                generated_id = f"{prefix}{max_id:05d}"
                setattr(instance, pk_field_name, generated_id)

# Register the signal for each model
for model in models_with_auto_id:
    create_signal(model)