import pytest
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from main_app.models import (
    Student, Professor, Course, Library, Schedule,
    Assignment, AssignmentSubmission, BookLending, CourseMaterial,
    Attendance, Department, Room, Enrollment, Announcement
)

@pytest.mark.django_db
class TestPersonModels:
    def test_student_creation(self):
        student = Student.objects.create(
            name="Test Student",
            email="test@student.com",
            password="password123",
            phone_number="1234567890",
            gender="Male",
            address="Test Address"
        )
        assert student.student_id.startswith('STU')
        assert student.name == "Test Student"
        assert str(student) == "Test Student"

    def test_professor_creation(self):
        dept = Department.objects.create(
            name="Computer Science",
            location="Building A"
        )
        professor = Professor.objects.create(
            name="Test Professor",
            email="test@professor.com",
            password="password123",
            phone_number="1234567890",
            gender="Female",
            address="Test Address",
            department=dept,
            specialization="Computer Science"
        )
        assert professor.professor_id.startswith('PRO')
        assert professor.specialization == "Computer Science"

@pytest.mark.django_db
class TestCourseRelatedModels:
    @pytest.fixture
    def course(self):
        return Course.objects.create(
            name="Test Course",
            description="Test Description"
        )

    def test_course_creation(self, course):
        assert course.course_id.startswith('COU')
        assert str(course) == "Test Course"

    def test_course_material(self, course):
        test_file = SimpleUploadedFile("test.txt", b"test content")
        material = CourseMaterial.objects.create(
            title="Test Material",
            file=test_file,
            course=course
        )
        assert material.material_id.startswith('MAT')
        assert str(material) == "Test Material - Test Course"

    def test_assignment(self, course):
        assignment = Assignment.objects.create(
            title="Test Assignment",
            description="Test Description",
            due_date=timezone.now().date(),
            course=course
        )
        assert assignment.assignment_id.startswith('ASS')
        assert str(assignment) == "Test Assignment - Test Course"

@pytest.mark.django_db
class TestLibraryModel:
    def test_library_book_creation(self):
        book = Library.objects.create(
            book_name="Test Book",
            book_description="Test Description",
            category="COMPUTER_SCIENCE",
            quantity=5,
            status="AVAILABLE"
        )
        assert book.book_id.startswith('LIB')
        assert str(book) == "Test Book"
        assert book.status == "AVAILABLE"

    def test_book_lending(self):
        book = Library.objects.create(
            book_name="Test Book",
            quantity=1,
            status="AVAILABLE"
        )
        student = Student.objects.create(
            name="Test Student",
            email="test@student.com",
            password="password123",
            phone_number="1234567890",
            gender="Male",
            address="Test Address"
        )
        lending = BookLending.objects.create(
            book=book,
            student=student
        )
        assert lending.borrow_date is not None
        assert lending.return_date is None

@pytest.mark.django_db
class TestScheduleAndAttendance:
    @pytest.fixture
    def setup_schedule(self):
        course = Course.objects.create(name="Test Course")
        room = Room.objects.create(
            room_type="Classroom",
            department=Department.objects.create(
                name="Test Department",
                location="Test Location"
            )
        )
        schedule = Schedule.objects.create(
            course=course,
            date=timezone.now().date(),
            time=timezone.now().time(),
            type="ON_CAMPUS",
            room=room
        )
        return course, schedule

    def test_schedule_creation(self, setup_schedule):
        course, schedule = setup_schedule
        assert schedule.schedule_id.startswith('SCH')
        assert str(schedule).startswith("Schedule for Test Course")

    def test_attendance_creation(self, setup_schedule):
        course, schedule = setup_schedule
        student = Student.objects.create(
            name="Test Student",
            email="test@student.com",
            password="password123",
            phone_number="1234567890",
            gender="Male",
            address="Test Address"
        )
        attendance = Attendance.objects.create(
            student=student,
            course=course,
            schedule=schedule,
            is_present=True
        )
        assert attendance.attendance_id.startswith('ATT')
        assert str(attendance).startswith("Test Student - Test Course")

@pytest.mark.django_db
class TestAnnouncement:
    def test_announcement_creation(self):
        announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Test Content",
            priority=1
        )
        assert announcement.title == "Test Announcement"
        assert announcement.priority == 1
        assert announcement.created_at is not None

@pytest.mark.django_db
class TestEnrollment:
    def test_enrollment_creation(self):
        student = Student.objects.create(
            name="Test Student",
            email="test@student.com",
            password="password123",
            phone_number="1234567890",
            gender="Male",
            address="Test Address"
        )
        course = Course.objects.create(name="Test Course")
        enrollment = Enrollment.objects.create(
            student=student,
            course=course
        )
        assert enrollment.enrollment_id.startswith('ENR')
        assert str(enrollment) == "Test Student - Test Course"
        assert enrollment.enrollment_date is not None
