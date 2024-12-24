from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

# Base abstract model
class Person(AbstractBaseUser):
    student_id = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        abstract = True

    def login(self, email, password):
        return True if self.email == email and self.password == password else False

    def logout(self):
        return "Logged Out"

    def edit_profile(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

# Models
class Student(Person):
    student_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    enrolled_courses = models.ManyToManyField("Course", through='Enrollment', related_name='students')

    def get_enrolled_courses(self):
        return self.enrolled_courses.all()

    def __str__(self):
        return self.name
    
    def check_assignments(self):
        return Assignment.objects.filter(course__in=self.enrolled_courses.all())

    def view_schedule(self):
        return Schedule.objects.filter(course__in=self.enrolled_courses.all())

    def view_attendance(self):
        return Attendance.objects.filter(student=self)

    def get_borrowed_books(self):
        return Library.objects.filter(booklending__student=self, booklending__return_date__isnull=True)

class Professor(Person):
    professor_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="professors")
    courses = models.ManyToManyField('Course', related_name="professors", blank=True)
    specialization = models.CharField(max_length=100)

    def check_assignments(self):
        return Assignment.objects.filter(course=self.course)

    def give_marks(self, assignment, marks):
        assignment.grade = marks
        assignment.save()
    
    def upload_course_material(self, title, file, course):
        """Upload course material for a specific course"""
        return CourseMaterial.objects.create(
            title=title,
            file=file,
            course=course
        )

    def mark_attendance(self, student, course, attendance_percent):
        """Mark attendance for a student in a course"""
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            course=course,
            defaults={'attendance_percent': attendance_percent}
        )
        if not created:
            attendance.attendance_percent = attendance_percent
            attendance.save()
        return attendance

    def grade_assignment(self, submission, grade):
        """Grade a student's assignment submission"""
        submission.grade = grade
        submission.save()

class Staff(Person):
    staff_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    position = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="staff")

    def add_book(self, book_name, category, quantity):
        Library.objects.create(book_name=book_name, category=category, quantity=quantity, status="Present")

    def assign_room(self, room, course):
        Schedule.objects.filter(course=course).update(room=room)

    def view_attendance(self):
        return Attendance.objects.all()

    def set_schedule(self, course, date, time):
        Schedule.objects.create(course=course, date=date, time=time, type="Class")

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
    
    book_id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    book_name = models.CharField(max_length=255)
    book_description = models.TextField(null=True)
    category = models.CharField(max_length=100)
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

    def borrow_book(self, student):
        if self.quantity > 0:
            BookLending.objects.create(book=self, student=student)
            self.quantity -= 1
            if self.quantity == 0:
                self.status = 'BORROWED'
            self.save()
            return True
        return False

    def return_book(self, student):
        lending = BookLending.objects.filter(
            book=self,
            student=student,
            return_date__isnull=True
        ).first()
        if lending:
            lending.return_date = timezone.now()
            lending.save()
            self.quantity += 1
            self.status = 'AVAILABLE'
            self.save()
            return True
        return False

class CourseMaterial(models.Model):
    material_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="materials")
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.name}"

    def save(self, *args, **kwargs):
        if not self.material_id:
            prefix = 'MAT'
            max_id = CourseMaterial.objects.count() + 1
            self.material_id = f"{prefix}{max_id:05d}"
        super().save(*args, **kwargs)

class AssignmentSubmission(models.Model):
    submission_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to='assignments/')
    grade = models.CharField(max_length=5, null=True, blank=True, default="Not Graded")
    submission_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.submission_id:
            prefix = 'SUB'
            max_id = AssignmentSubmission.objects.count() + 1
            self.submission_id = f"{prefix}{max_id:05d}"
        super().save(*args, **kwargs)

class Room(models.Model):
    room_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    room_type = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="rooms")

class GradingQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, submission):
        self.queue.append(submission)

    def dequeue(self):
        return self.queue.pop(0) if self.queue else None

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
    schedule_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    time = models.TimeField()
    type = models.CharField(max_length=50)
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, related_name="schedules")

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

# Define the prefix mapping
prefix_mapping = {
    'Student': 'STU',
    'Professor': 'PRO',
    'Staff': 'STA',
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
    Student, Professor, Staff, Library, Room, Department, Course,
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