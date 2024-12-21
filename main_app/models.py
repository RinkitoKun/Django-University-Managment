from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib import admin

# Base abstract model
class Person(AbstractBaseUser):
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


class Professor(Person):
    professor_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="professors")
    course = models.OneToOneField('Course', on_delete=models.SET_NULL, null=True, blank=True, related_name="professor")
    specialization = models.CharField(max_length=100)

    def check_assignments(self):
        return Assignment.objects.filter(course=self.course)

    def give_marks(self, assignment, marks):
        assignment.grade = marks
        assignment.save()


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


class BookFactory:
    @staticmethod
    def create_book(book_name, category, quantity):
        return Library(book_name=book_name, category=category, quantity=quantity, status="Present")

class Library(models.Model):
    book_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=[('Borrowed', 'Borrowed'), ('Present', 'Present')])
    borrower = models.ForeignKey('Student', null=True, blank=True, on_delete=models.SET_NULL, related_name="borrowed_books")

class BorrowRequestQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, book, student):
        self.queue.append((book, student))

    def dequeue(self):
        return self.queue.pop(0) if self.queue else None

class CourseMaterial(models.Model):
    material_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="materials")

class AssignmentSubmission(models.Model):
    submission_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to='assignments/')
    grade = models.CharField(max_length=5, null=True, blank=True, default="Not Graded")
    submission_date = models.DateTimeField(auto_now_add=True)

class Room(models.Model):
    room_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    room_type = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
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
    course = models.OneToOneField('Course', on_delete=models.CASCADE, related_name="schedule")
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
    grade = models.CharField(max_length=5, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="assignments")


class Attendance(models.Model):
    attendance_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendances")
    attendance_percent = models.FloatField()


class Enrollment(models.Model):
    enrollment_id = models.CharField(
        max_length=20, primary_key=True, unique=True, blank=True, editable=False
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

models_with_auto_id = [
    Student, Professor, Staff, Library, Room, Department, Course,
    Schedule, Assignment, Attendance, Enrollment
]

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
}

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