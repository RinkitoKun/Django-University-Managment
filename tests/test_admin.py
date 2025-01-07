import pytest
from django.contrib.admin.sites import site
from django.apps import apps
from main_app.models import (
    Student, Professor, Course, Library, Schedule,
    Assignment, AssignmentSubmission, Room, Department, Attendance,
    Enrollment, CourseMaterial, BookLending, Announcement
)

@pytest.mark.parametrize("model, admin_class", [
    (Student, 'StudentAdmin'),
    (Professor, 'ProfessorAdmin'),
    (Course, 'CourseAdmin'),
    (Library, 'LibraryAdmin'),
    (Schedule, 'ScheduleAdmin'),
    (Assignment, 'AssignmentAdmin'),
    (AssignmentSubmission, 'AssignmentSubmissionAdmin'),
    (Room, 'RoomAdmin'),
    (Department, 'DepartmentAdmin'),
    (Attendance, 'AttendanceAdmin'),
    (Enrollment, 'EnrollmentAdmin'),
    (CourseMaterial, 'CourseMaterialAdmin'),
    (BookLending, 'BookLendingAdmin'),
    (Announcement, 'AnnouncementAdmin'),
])
def test_admin_registration(model, admin_class):
    """Test if the models are registered in the admin site with correct admin classes."""
    assert site.is_registered(model), f"{model.__name__} is not registered in admin site"
    admin_instance = site._registry.get(model)
    assert admin_instance is not None, f"{model.__name__} has no admin instance"
    assert admin_instance.__class__.__name__ == admin_class, (
        f"{model.__name__} admin class mismatch: expected {admin_class}, got {admin_instance.__class__.__name__}"
    )

@pytest.mark.parametrize("model, expected_fields", [
    (Student, ['name', 'email', 'student_id', 'get_enrolled_courses']),
    (Professor, ['name', 'email', 'professor_id', 'get_department', 'get_courses']), 
    (Library, ['book_id', 'book_name', 'category', 'quantity', 'status']),
    (BookLending, ['book', 'student', 'borrow_date', 'return_date']),
])
def test_list_display_fields(model, expected_fields):
    """Test if list_display fields are configured correctly in the admin class."""
    admin_instance = site._registry.get(model)
    assert admin_instance, f"{model.__name__} is not registered in admin site"
    assert hasattr(admin_instance, 'list_display'), f"{model.__name__} has no list_display attribute"
    assert list(admin_instance.list_display) == expected_fields, (
        f"{model.__name__} list_display mismatch: expected {expected_fields}, got {list(admin_instance.list_display)}"
    )

@pytest.mark.parametrize("model, expected_fields", [
    (Student, ['name', 'email', 'student_id']),
    (Professor, ['name', 'email', 'professor_id']),
    (Library, ['book_name', 'category', 'book_id']),
    (BookLending, ['book__book_name', 'student__name']),
])
def test_search_fields(model, expected_fields):
    """Test if search_fields are configured correctly in the admin class."""
    admin_instance = site._registry.get(model)
    assert admin_instance, f"{model.__name__} is not registered in admin site"
    assert hasattr(admin_instance, 'search_fields'), f"{model.__name__} has no search_fields attribute"
    assert list(admin_instance.search_fields) == expected_fields, (
        f"{model.__name__} search_fields mismatch: expected {expected_fields}, got {list(admin_instance.search_fields)}"
    )