from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('student/<str:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('professor/<str:professor_id>/', views.professor_dashboard, name='professor_dashboard'),
    path('student/<str:student_id>/library/', views.library_view, name='library'),
    path('student/<str:student_id>/library/borrow/<str:book_id>/', views.borrow_book, name='borrow_book'),
    path('student/<str:student_id>/library/return/<str:book_id>/', views.return_book, name='return_book'),
    path('student/<str:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('student/<str:student_id>/course/<str:course_id>/', views.course_detail, name='course_detail'),
    path('student/<str:student_id>/course/<str:course_id>/materials/', views.course_materials, name='course_materials'),
    path('student/<str:student_id>/course/<str:course_id>/schedule/', views.course_schedule, name='course_schedule'),
    path('student/<str:student_id>/course/<str:course_id>/assignment/<str:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    
]
