# file: views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime
from django.db import models

from .models import (
    Student, Professor, Course, Library, Schedule,
    Assignment, AssignmentSubmission, BookLending, CourseMaterial, Attendance, Announcement
)
from .forms import AssignmentSubmissionForm, PasswordResetForm


#Password Reset Request
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            student = Student.objects.filter(email=email).first()
            professor = Professor.objects.filter(email=email).first()
            
            if student:
                return redirect('password_reset_form', student_id=student.student_id)
            elif professor:
                return redirect('password_reset_form', professor_id=professor.professor_id)
            else:
                messages.error(request, "Email does not exist in our records.")
                return render(request, 'password_reset_request.html', {'form': form})
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_request.html', {'form': form})

#Password Reset Form
def password_reset_form(request, student_id=None, professor_id=None):
    if professor_id:
        user = get_object_or_404(Professor, professor_id=professor_id)
    else:
        user = get_object_or_404(Student, student_id=student_id)
        
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and new_password == confirm_password:
            user.password = new_password
            user.save()
            messages.success(request, "Password reset successfully.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'password_reset_form.html', {'user': user})



#Announcement View
def announcements_view(request,student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        announcements = Announcement.objects.order_by('priority', '-created_at') 
        return render(request, 'student/announcement/announcements.html', {'announcements': announcements,'student': student})
    except Student.DoesNotExist:
        messages.error(request, "Student not found!")
        return redirect('home')    

#Book Search View
def book_search_view(request,student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        query = request.GET.get('q')
        books = Library.objects.all()  # Default: show all books
        
        if query:  # Only filter if query exists and not empty
            books = Library.objects.filter(book_name__icontains=query)
            
        return render(request, 'student/library/library.html', {
            'books': books, 
            'query': query,
            'student': student
        })
       
    except Student.DoesNotExist:
        messages.error(request, "Student not found!")
        return redirect('home')

# Login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the user is a Student
        student = Student.objects.filter(email=email).first()
        if student and student.password == password:  # Assuming password is hashed
            return redirect('student_dashboard', student_id=student.student_id)

        # Check if the user is a Professor
        professor = Professor.objects.filter(email=email).first()
        if professor and professor.password == password:  # Assuming password is hashed
            return redirect('professor_dashboard', professor_id=professor.professor_id)

        # Invalid credentials
        messages.error(request, "Invalid email or password.")
        return redirect('login')

    return render(request, 'login.html')

# Add this new view function
def logout_view(request):
    if request.method == 'POST':
        return redirect('login')
    return redirect(request.META.get('HTTP_REFERER', 'login'))

# Professor dashboard
def professor_dashboard(request, professor_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    courses = professor.courses.all()
    return render(request, 'professor/professor_dashboard.html', {
        'professor': professor,
        'courses': courses
    })

# Library view
def library(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    search_query = request.GET.get('search', '')
    
    # Initialize queryset
    books = Library.objects.all()
    
    # Apply search filter if search_query exists
    if search_query:
        books = books.filter(
            models.Q(book_name__icontains=search_query) |
            models.Q(book_description__icontains=search_query) |
            models.Q(category__icontains=search_query)
        )
    
    context = {
        'student': student,
        'books': books,
        'search_query': search_query
    }
    return render(request, 'student/library/library.html', context)

# Borrow a book
def borrow_book(request, student_id, book_id):
    try:
        student = Student.objects.get(student_id=student_id)
        book = Library.objects.get(book_id=book_id)
        
        # Check if student already has this book
        existing_borrow = BookLending.objects.filter(
            student=student,
            book=book,
            return_date__isnull=True
        ).exists()
        
        if existing_borrow:
            messages.error(request, "You have already borrowed this book")
            return redirect('library', student_id=student_id)
            
        if book.quantity > 0:
            # Create lending record
            BookLending.objects.create(
                student=student,
                book=book
            )
            
            # Update book status
            book.quantity -= 1
            if book.quantity == 0:
                book.status = 'BORROWED'
            book.save()
            
            messages.success(request, f"Successfully borrowed {book.book_name}")
        else:
            messages.error(request, "Book not available for borrowing")
            
        return redirect('library', student_id=student_id)
        
    except Student.DoesNotExist:
        messages.error(request, "Student not found")
        return redirect('home')
    except Library.DoesNotExist:
        messages.error(request, "Book not found")
        return redirect('library', student_id=student_id)

# Return a book
def return_book(request, student_id, book_id):
    try:
        student = Student.objects.get(student_id=student_id)
        book = Library.objects.get(book_id=book_id)
        
        # Find active lending
        lending = BookLending.objects.filter(
            student=student,
            book=book,
            return_date__isnull=True
        ).first()
        
        if lending:
            # Update lending record
            lending.return_date = timezone.now()
            lending.save()
            
            # Update book status
            book.quantity += 1
            book.status = 'AVAILABLE'
            book.save()
            
            messages.success(request, f"Successfully returned {book.book_name}")
        else:
            messages.error(request, "No active borrowing found for this book")
            
        return redirect('library', student_id=student_id)
        
    except Student.DoesNotExist:
        messages.error(request, "Student not found")
        return redirect('home')
    except Library.DoesNotExist:
        messages.error(request, "Book not found")
        return redirect('library', student_id=student_id)

# Student dashboard

def student_dashboard(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    courses = student.enrolled_courses.all()
    
    # Calculate attendance records with percentages
    attendance_records = []
    for course in courses:
        total_classes = Attendance.objects.filter(course=course, student=student).count()
        if total_classes > 0:
            present_classes = Attendance.objects.filter(
                course=course, 
                student=student,
                is_present=True
            ).count()
            attendance_percent = (present_classes / total_classes) * 100
        else:
            attendance_percent = 0
            
        attendance_records.append({
            'course': course,
            'attendance_percent': round(attendance_percent, 2)
        })

    # Get current datetime in the user's timezone
    current_datetime = timezone.now()
    
    # Get upcoming schedules
    schedules = Schedule.objects.filter(
        course__in=courses,
        date__gte=current_datetime.date()
    ).select_related('course', 'room').order_by('date', 'time')
    
    # Filter out past schedules from today
    today_schedules = []
    for schedule in schedules:
        schedule_datetime = timezone.make_aware(
            datetime.combine(schedule.date, schedule.time)
        )
        if schedule_datetime > current_datetime:
            today_schedules.append(schedule)
    
    context = {
        'student': student,
        'courses': courses,
        'attendance_records': attendance_records,  # Changed from attendance to attendance_records
        'schedules': today_schedules,
    }

    return render(request, 'student/student_dashboard.html', context)

# Course detail view
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Course, Student, Assignment, AssignmentSubmission

def course_detail(request, student_id, course_id):
    student = get_object_or_404(Student, student_id=student_id)
    course = get_object_or_404(Course, course_id=course_id)
    
    # Get course materials
    materials = course.materials.all()
    
    # Get assignments with prefetched submissions
    assignments = Assignment.objects.filter(course=course).prefetch_related(
        'submissions'
    )
    
    context = {
        'student': student,
        'course': course,
        'materials': materials,
        'assignments': assignments,
        'today': timezone.now().date(),
    }
    return render(request, 'student/course/course_detail.html', context)

# Professor Course Management Views
def professor_course_detail(request, professor_id, course_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    return render(request, 'professor/course/course_detail.html', {
        'professor': professor,
        'course': course
    })

def course_materials_manage(request, professor_id, course_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    materials = CourseMaterial.objects.filter(course=course).order_by('-upload_date')

    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        
        if title and file:
            try:
                material = CourseMaterial(
                    title=title,
                    file=file,
                    course=course
                )
                material.save()
                messages.success(request, 'Material uploaded successfully')
            except Exception as e:
                messages.error(request, f'Error uploading material: {str(e)}')
            
            return redirect('course_materials_manage', professor_id=professor_id, course_id=course_id)

    return render(request, 'professor/course/course_materials.html', {
        'professor': professor,
        'course': course,
        'materials': materials
    })

def delete_course_material(request, professor_id, course_id, material_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    material = get_object_or_404(CourseMaterial, material_id=material_id, course=course)
    
    material.file.delete()  
    material.delete()       
    messages.success(request, 'Material deleted successfully')
    
    return redirect('course_materials_manage', professor_id=professor_id, course_id=course_id)

def update_course_material(request, professor_id, course_id, material_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    material = get_object_or_404(CourseMaterial, material_id=material_id, course=course)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        new_file = request.FILES.get('file')
        
        if title:
            material.title = title
        if new_file:
            material.file.delete()  # Delete old file
            material.file = new_file
        
        material.save()
        messages.success(request, 'Material updated successfully')
        return redirect('course_materials_manage', professor_id=professor_id, course_id=course_id)

    return render(request, 'professor/course/update_material.html', {
        'professor': professor,
        'course': course,
        'material': material
    })

# Attendance Management Views
def manage_attendance(request, professor_id, course_id):
    try:
        professor = get_object_or_404(Professor, professor_id=professor_id)
        course = get_object_or_404(Course, course_id=course_id)
        
        schedules = Schedule.objects.filter(course=course).order_by('-date', '-time')
        
        context = {
            'professor': professor,
            'course': course,
            'schedules': schedules,
        }
        
        return render(request, 'professor/attendance/manage.html', context)
    except Exception as e:
        messages.error(request, f"Error accessing attendance page: {str(e)}")
        return redirect('professor_dashboard', professor_id=professor_id)

def mark_attendance(request, professor_id, course_id, schedule_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    schedule = get_object_or_404(Schedule, schedule_id=schedule_id)
    students = course.students.all()

    if request.method == 'POST':
        present_students = request.POST.getlist('attendance[]')
        attendance_dict = {str(student.student_id): False for student in students}

        for student_id in present_students:
            attendance_dict[student_id] = True

        for student in students:
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                course=course,
                schedule=schedule,
                defaults={'attendance_percent': 0}
            )
            attendance.is_present = attendance_dict[str(student.student_id)]
            attendance.save()

        messages.success(request, 'Attendance marked successfully')
        return redirect('manage_attendance', professor_id=professor_id, course_id=course_id)

    attendance_records = Attendance.objects.filter(
        student__in=students,
        course=course,
        schedule=schedule
    )
    attendance_dict = {str(a.student.student_id): a.is_present for a in attendance_records}

    return render(request, 'professor/attendance/mark.html', {
        'professor': professor,
        'course': course,
        'schedule': schedule,
        'students': students,
        'attendance_dict': attendance_dict
    })

def manage_assignments(request, professor_id, course_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    assignments = Assignment.objects.filter(course=course).order_by('due_date')

    return render(request, 'professor/assignments/manage.html', {
        'professor': professor,
        'course': course,
        'assignments': assignments
    })

def add_assignment(request, professor_id, course_id):
    if request.method == 'POST':
        professor = get_object_or_404(Professor, professor_id=professor_id)
        course = get_object_or_404(Course, course_id=course_id)
        
        try:
            assignment = Assignment(
                title=request.POST['title'],
                description=request.POST['description'],
                due_date=request.POST['due_date'],
                course=course
            )
            if 'file' in request.FILES:
                assignment.file = request.FILES['file']
            assignment.save()
            messages.success(request, 'Assignment added successfully')
        except Exception as e:
            messages.error(request, f'Error adding assignment: {str(e)}')
        
    return redirect('manage_assignments', professor_id=professor_id, course_id=course_id)

def delete_assignment(request, professor_id, course_id, assignment_id):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully')
    
    return redirect('manage_assignments', professor_id=professor_id, course_id=course_id)

def update_assignment(request, professor_id, course_id, assignment_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)

    if request.method == 'POST':
        try:
            assignment.title = request.POST.get('title')
            assignment.description = request.POST.get('description')
            assignment.due_date = request.POST.get('due_date')
            
            if 'file' in request.FILES:
                if assignment.file:
                    assignment.file.delete()
                assignment.file = request.FILES['file']
            
            assignment.save()
            messages.success(request, 'Assignment updated successfully')
        except Exception as e:
            messages.error(request, f'Error updating assignment: {str(e)}')
        
        return redirect('manage_assignments', professor_id=professor_id, course_id=course_id)

    return render(request, 'professor/assignments/edit.html', {
        'professor': professor,
        'course': course,
        'assignment': assignment
    })

def save_grades(request, professor_id, course_id, assignment_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    
    if request.method == 'POST':
        try:
            for key, grade in request.POST.items():
                if key.startswith('grade_'):
                    submission_id = key.replace('grade_', '')
                    submission = AssignmentSubmission.objects.get(submission_id=submission_id)
                    submission.grade = grade
                    submission.save()
            messages.success(request, 'Grades saved successfully')
            return redirect('manage_assignments', professor_id=professor_id, course_id=course_id)
        except Exception as e:
            messages.error(request, f'Error saving grades: {str(e)}')
    
    return render(request, 'professor/assignments/grade.html', {
        'professor': professor,
        'course': course,
        'assignment': assignment,
        'submissions': submissions
    })

class AssignmentSubmissionFactory:
    @staticmethod
    def create_submission(assignment, student, file):
        return AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student,
            file=file
        )

def submit_assignment(request, student_id, course_id, assignment_id):
    student = get_object_or_404(Student, pk=student_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    if request.method == 'POST':
        if assignment.due_date < timezone.now().date():
            return JsonResponse({'success': False, 'error': 'The due date has passed. You cannot submit or edit the assignment.'})

        submission_file = request.FILES.get('submission_file')
        if submission_file:
            # Check if submission already exists
            existing_submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=student
            ).first()
            
            if existing_submission:
                existing_submission.file.delete()
                existing_submission.file = submission_file
                existing_submission.save()
                return JsonResponse({'success': True, 'message': 'Assignment updated successfully', 'file_url': existing_submission.file.url, 'file_name': existing_submission.file.name, 'assignment_id': assignment_id})
            else:
                # Create new submission using factory
                submission = AssignmentSubmissionFactory.create_submission(
                    assignment=assignment,
                    student=student,
                    file=submission_file
                )
                return JsonResponse({'success': True, 'message': 'Assignment submitted successfully', 'file_url': submission.file.url, 'file_name': submission.file.name, 'assignment_id': assignment_id})
        else:
            return JsonResponse({'success': False, 'error': 'No file uploaded'})
                
    elif request.method == 'DELETE':
        existing_submission = AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=student
        ).first()
        if existing_submission:
            existing_submission.file.delete()
            existing_submission.delete()
            return JsonResponse({'success': True, 'message': 'Assignment deleted successfully', 'assignment_id': assignment_id})
        else:
            return JsonResponse({'success': False, 'error': 'No submission found to delete'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
