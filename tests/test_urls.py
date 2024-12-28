import pytest
from django.urls import resolve, reverse
from main_app import views

@pytest.mark.django_db
class TestUrls:
    def test_login_url(self):
        url = reverse('login')
        assert resolve(url).func == views.login_view

    def test_logout_url(self):
        url = reverse('logout')
        assert resolve(url).func == views.logout_view

    def test_student_urls(self):
        # Test student dashboard
        url = reverse('student_dashboard', args=['STU123'])
        assert resolve(url).func == views.student_dashboard

        # Test announcements
        url = reverse('announcements', args=['STU123'])
        assert resolve(url).func == views.announcements_view

        # Test library related URLs
        url = reverse('book_search', args=['STU123'])
        assert resolve(url).func == views.book_search_view

        url = reverse('library', args=['STU123'])
        assert resolve(url).func == views.library

        url = reverse('borrow_book', args=['STU123', 'LIB123'])
        assert resolve(url).func == views.borrow_book

        url = reverse('return_book', args=['STU123', 'LIB123'])
        assert resolve(url).func == views.return_book

        # Test course related URLs
        url = reverse('course_detail', args=['STU123', 'COU123'])
        assert resolve(url).func == views.course_detail

        url = reverse('submit_assignment', args=['STU123', 'COU123', 'ASS123'])
        assert resolve(url).func == views.submit_assignment

    def test_professor_urls(self):
        # Test professor dashboard
        url = reverse('professor_dashboard', args=['PRO123'])
        assert resolve(url).func == views.professor_dashboard

        # Test course detail
        url = reverse('professor_course_detail', args=['PRO123', 'COU123'])
        assert resolve(url).func == views.professor_course_detail

        # Test course materials management
        url = reverse('course_materials_manage', args=['PRO123', 'COU123'])
        assert resolve(url).func == views.course_materials_manage

        url = reverse('delete_course_material', args=['PRO123', 'COU123', 'MAT123'])
        assert resolve(url).func == views.delete_course_material

        url = reverse('update_course_material', args=['PRO123', 'COU123', 'MAT123'])
        assert resolve(url).func == views.update_course_material

    def test_assignment_management_urls(self):
        # Test assignment management URLs
        url = reverse('manage_assignments', args=['PRO123', 'COU123'])
        assert resolve(url).func == views.manage_assignments

        url = reverse('add_assignment', args=['PRO123', 'COU123'])
        assert resolve(url).func == views.add_assignment

        url = reverse('delete_assignment', args=['PRO123', 'COU123', 'ASS123'])
        assert resolve(url).func == views.delete_assignment

        url = reverse('update_assignment', args=['PRO123', 'COU123', 'ASS123'])
        assert resolve(url).func == views.update_assignment

        url = reverse('save_grades', args=['PRO123', 'COU123', 'ASS123'])
        assert resolve(url).func == views.save_grades

    def test_attendance_management_urls(self):
        # Test attendance management URLs
        url = reverse('manage_attendance', args=['PRO123', 'COU123'])
        assert resolve(url).func == views.manage_attendance

        url = reverse('mark_attendance', args=['PRO123', 'COU123', 'SCH123'])
        assert resolve(url).func == views.mark_attendance

    def test_password_reset_urls(self):
        # Test password reset URLs
        url = reverse('password_reset_request')
        assert resolve(url).func == views.password_reset_request

        url = reverse('password_reset_form', args=['PRO123'])
        assert resolve(url).func == views.password_reset_form

        url = reverse('password_reset_form', args=['STU123'])
        assert resolve(url).func == views.password_reset_form
