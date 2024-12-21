from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('student/<int:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('professor/<int:professor_id>/', views.professor_dashboard, name='professor_dashboard'),
    path('student/<int:student_id>/library/', views.library_view, name='library'),
    path('student/<int:student_id>/library/borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('student/<int:student_id>/library/return/<int:book_id>/', views.return_book, name='return_book'),
    path('student/<int:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('student/<int:student_id>/course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('student/<int:student_id>/course/<int:course_id>/materials/', views.course_materials, name='course_materials'),
    path('student/<int:student_id>/course/<int:course_id>/schedule/', views.course_schedule, name='course_schedule'),
    path('student/<int:student_id>/course/<int:course_id>/assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
]
