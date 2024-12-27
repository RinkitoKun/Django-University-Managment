from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #Student Announcement
     path('student/<str:student_id>/announcements/', views.announcements_view, name='announcements'),

    # Student Routes
    path('student/<str:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('student/<str:student_id>/library/books/', views.book_search_view, name='book_search'),
    path('student/<str:student_id>/library/', views.library, name='library'),
    path('student/<str:student_id>/library/borrow/<str:book_id>/', views.borrow_book, name='borrow_book'),
    path('student/<str:student_id>/library/return/<str:book_id>/', views.return_book, name='return_book'),
    path('student/<str:student_id>/course/<str:course_id>/', views.course_detail, name='course_detail'),
    path('student/<str:student_id>/course/<str:course_id>/assignment/<str:assignment_id>/submit/', 
         views.submit_assignment, name='submit_assignment'),

    # Professor Routes
    path('professor/<str:professor_id>/', views.professor_dashboard, name='professor_dashboard'),
    path('professor/<str:professor_id>/course/<str:course_id>/', 
         views.professor_course_detail, name='professor_course_detail'),
    
    # Course Material Management
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
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/<str:assignment_id>/update/', 
         views.update_assignment, name='update_assignment'),
    path('professor/<str:professor_id>/course/<str:course_id>/assignments/<str:assignment_id>/grades/', 
         views.save_grades, name='save_grades'),  # Updated URL pattern for grading

    # Attendance Management
    path('professor/<str:professor_id>/course/<str:course_id>/attendance/', 
         views.manage_attendance, name='manage_attendance'),
    path('professor/<str:professor_id>/course/<str:course_id>/attendance/<str:schedule_id>/', 
         views.mark_attendance, name='mark_attendance'),

      #Password Reset
     path('password_reset/', views.password_reset_request, name='password_reset_request'),
     path('password_reset_form/professor/<str:professor_id>', views.password_reset_form, name='password_reset_form'),
     path('password_reset_form/student/<str:student_id>', views.password_reset_form, name='password_reset_form'),
]
