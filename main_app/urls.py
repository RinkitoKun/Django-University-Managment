from django.urls import path
from . import views

urlpatterns = [
    # Login
    path('', views.login_view, name='login'),
    
    # Student Dashboard
    path('student/<str:student_id>/', views.student_dashboard, name='student_dashboard'),

    # Professor Dashboard
    path('professor/<str:professor_id>/', views.professor_dashboard, name='professor_dashboard'),

    # Library Views
    path('student/<str:student_id>/library/', views.library_view, name='library'),
    path('student/<str:student_id>/library/borrow/<str:book_id>/', views.borrow_book, name='borrow_book'),
    path('student/<str:student_id>/library/return/<str:book_id>/', views.return_book, name='return_book'),

    # Course Details
    path('student/<str:student_id>/course/<str:course_id>/', views.course_detail, name='course_detail'),
    path('student/<str:student_id>/course/<str:course_id>/materials/', views.course_materials, name='course_materials'),
    path('student/<str:student_id>/course/<str:course_id>/schedule/', views.course_schedule, name='course_schedule'),

    # Assignment Details
    path('student/<str:student_id>/course/<str:course_id>/assignment/<str:assignment_id>/', 
         views.assignment_detail, name='assignment_detail'),
    path('student/<str:student_id>/course/<str:course_id>/assignment/<str:assignment_id>/submit/',
         views.submit_assignment, name='submit_assignment'),

    # Professor Course Management
    path('professor/<str:professor_id>/course/<str:course_id>/', 
         views.professor_course_detail, name='professor_course_detail'),
    path('professor/<str:professor_id>/course/<str:course_id>/materials/', 
         views.course_materials_manage, name='course_materials_manage'),
    path('professor/<str:professor_id>/course/<str:course_id>/materials/<str:material_id>/delete/', 
         views.delete_course_material, name='delete_course_material'),
    path('professor/<str:professor_id>/course/<str:course_id>/materials/<str:material_id>/update/', 
         views.update_course_material, name='update_course_material'),

    # Assignment Management
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/', 
         views.manage_assignments, name='manage_assignments'),
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/add/', 
         views.add_assignment, name='add_assignment'),
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/<str:assignment_id>/delete/', 
         views.delete_assignment, name='delete_assignment'),
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/<str:assignment_id>/grade/', 
         views.grade_submissions, name='grade_submissions'),
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/<str:assignment_id>/update/', 
         views.update_assignment, name='update_assignment'),
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/<str:assignment_id>/save-grades/', 
         views.save_grades, name='save_grades'),
    path('professor/<int:professor_id>/course/<int:course_id>/assignments/manage/', 
         views.manage_assignments, name='manage_assignments'),

    # Attendance Management
    path('professor/<str:professor_id>/course/<str:course_id>/attendance/<str:schedule_id>/', 
         views.mark_attendance, name='mark_attendance'),
    path('professor/<str:professor_id>/course/<str:course_id>/attendance/', 
         views.manage_attendance, name='manage_attendance'),

    # Add Schedule
    path('professor/<int:professor_id>/course/<int:course_id>/schedule/add/', 
         views.add_schedule, name='add_schedule'),
]
