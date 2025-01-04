import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from main_app.models import (
    Student, Professor, Course, Library, Schedule,
    Assignment, AssignmentSubmission, BookLending, Department,
    CourseMaterial, Attendance, Announcement
)

@pytest.fixture
def student():
    return Student.objects.create(
        name="Test Student",
        email="test@student.com",
        password="password123",
        phone_number="1234567890",
        gender="Male",
        address="Test Address"
    )

@pytest.fixture
def professor():
    dept = Department.objects.create(name="Test Department", location="Test Location")
    return Professor.objects.create(
        name="Test Professor",
        email="test@professor.com",
        password="password123",
        phone_number="1234567890",
        gender="Male",
        address="Test Address",
        department=dept,
        specialization="Test Specialization"
    )

@pytest.fixture
def course():
    return Course.objects.create(
        name="Test Course",
        description="Test Description"
    )

@pytest.mark.django_db
class TestAuthenticationViews:
    def test_login_view_get(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'login.html' in [t.name for t in response.templates]

    def test_login_view_post_student(self, client, student):
        response = client.post(reverse('login'), {
            'email': student.email,
            'password': student.password
        })
        assert response.status_code == 302
        assert response.url == reverse('student_dashboard', args=[student.student_id])

    def test_login_view_post_professor(self, client, professor):
        response = client.post(reverse('login'), {
            'email': professor.email,
            'password': professor.password
        })
        assert response.status_code == 302
        assert response.url == reverse('professor_dashboard', args=[professor.professor_id])

    def test_logout_view(self, client):
        response = client.post(reverse('logout'))
        assert response.status_code == 302
        assert response.url == reverse('login')

@pytest.mark.django_db
class TestStudentViews:
    def test_student_dashboard(self, client, student, course):
        student.enrolled_courses.add(course)
        response = client.get(reverse('student_dashboard', args=[student.student_id]))
        assert response.status_code == 200
        assert 'student/student_dashboard.html' in [t.name for t in response.templates]

    def test_course_detail(self, client, student, course):
        student.enrolled_courses.add(course)
        response = client.get(reverse('course_detail', args=[student.student_id, course.course_id]))
        assert response.status_code == 200
        assert 'student/course/course_detail.html' in [t.name for t in response.templates]

    @pytest.mark.parametrize('query', ['', 'test'])
    def test_book_search_view(self, client, student, query):
        response = client.get(
            reverse('book_search', args=[student.student_id]),
            {'q': query}
        )
        assert response.status_code == 200
        assert 'student/library/library.html' in [t.name for t in response.templates]

@pytest.mark.django_db
class TestProfessorViews:
    def test_professor_dashboard(self, client, professor, course):
        professor.courses.add(course)
        response = client.get(reverse('professor_dashboard', args=[professor.professor_id]))
        assert response.status_code == 200
        assert 'professor/professor_dashboard.html' in [t.name for t in response.templates]

    def test_manage_assignments(self, client, professor, course):
        professor.courses.add(course)
        response = client.get(reverse('manage_assignments', args=[professor.professor_id, course.course_id]))
        assert response.status_code == 200
        assert 'professor/assignments/manage.html' in [t.name for t in response.templates]

    def test_add_assignment(self, client, professor, course):
        professor.courses.add(course)
        data = {
            'title': 'Test Assignment',
            'description': 'Test Description',
            'due_date': timezone.now().date(),
        }
        response = client.post(reverse('add_assignment', args=[professor.professor_id, course.course_id]), data)
        assert response.status_code == 302
        assert Assignment.objects.filter(title='Test Assignment').exists()

@pytest.mark.django_db
class TestLibraryViews:
    @pytest.fixture
    def book(self):
        return Library.objects.create(
            book_name="Test Book",
            quantity=1,
            status="AVAILABLE"
        )

    def test_borrow_book(self, client, student, book):
        response = client.post(reverse('borrow_book', args=[student.student_id, book.book_id]))
        assert response.status_code == 302
        assert BookLending.objects.filter(student=student, book=book).exists()

    def test_return_book(self, client, student, book):
        lending = BookLending.objects.create(student=student, book=book)
        response = client.post(reverse('return_book', args=[student.student_id, book.book_id]))
        assert response.status_code == 302
        lending.refresh_from_db()
        assert lending.return_date is not None

@pytest.mark.django_db
class TestAttendanceViews:
    @pytest.fixture
    def schedule(self, course):
        return Schedule.objects.create(
            course=course,
            date=timezone.now().date(),
            time=timezone.now().time(),
            type="ON_CAMPUS"
        )

    def test_manage_attendance(self, client, professor, course):
        professor.courses.add(course)
        response = client.get(reverse('manage_attendance', args=[professor.professor_id, course.course_id]))
        assert response.status_code == 200
        assert 'professor/attendance/manage.html' in [t.name for t in response.templates]

    def test_mark_attendance(self, client, professor, course, student, schedule):
        professor.courses.add(course)
        student.enrolled_courses.add(course)
        data = {'attendance[]': [student.student_id]}
        response = client.post(
            reverse('mark_attendance', args=[professor.professor_id, course.course_id, schedule.schedule_id]),
            data
        )
        assert response.status_code == 302
        assert Attendance.objects.filter(student=student, course=course, is_present=True).exists()

@pytest.mark.django_db
class TestAssignmentSubmissionViews:
    @pytest.fixture
    def assignment(self, course):
        return Assignment.objects.create(
            title="Test Assignment",
            description="Test Description",
            due_date=timezone.now().date(),
            course=course
        )

    def test_submit_assignment(self, client, student, course, assignment):
        student.enrolled_courses.add(course)
        file_content = b"test content"
        test_file = SimpleUploadedFile("test.txt", file_content)
        
        response = client.post(
            reverse('submit_assignment', args=[student.student_id, course.course_id, assignment.assignment_id]),
            {'submission_file': test_file},
            format='multipart'
        )
        
        assert response.status_code == 200
        assert AssignmentSubmission.objects.filter(student=student, assignment=assignment).exists()

@pytest.mark.django_db
class TestAnnouncementViews:
    def test_announcements_view(self, client, student):
        announcement = Announcement.objects.create(
            title="Test Announcement",
            content="Test Content",
            priority=1
        )
        response = client.get(reverse('announcements', args=[student.student_id]))
        assert response.status_code == 200
        assert 'student/announcement/announcements.html' in [t.name for t in response.templates]
        assert announcement in response.context['announcements']

@pytest.mark.django_db
class TestPasswordResetViews:
    def test_password_reset_request_invalid_email(self, client):
        response = client.post(reverse('password_reset_request'), {
            'email': 'nonexistent@example.com'
        })
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == "Email does not exist in our records."

    def test_password_reset_request_valid_student_email(self, client, student):
        response = client.post(reverse('password_reset_request'), {
            'email': student.email
        })
        assert response.status_code == 302
        assert response.url == reverse('password_reset_form', args=[student.student_id])

    def test_password_reset_request_valid_professor_email(self, client, professor):
        response = client.post(reverse('password_reset_request'), {
            'email': professor.email
        })
        assert response.status_code == 302
        assert response.url == reverse('password_reset_form', kwargs={'professor_id': professor.professor_id})
