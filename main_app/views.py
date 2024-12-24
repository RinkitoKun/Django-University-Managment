# file: views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime

from .models import (
    Student, Professor, Course, Library, Schedule,
    Assignment, AssignmentSubmission, GradingQueue, BookLending, CourseMaterial, Attendance
)
from .forms import AssignmentSubmissionForm

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

# Professor dashboard
def professor_dashboard(request, professor_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    courses = professor.courses.all()
    return render(request, 'professor/professor_dashboard.html', {
        'professor': professor,
        'courses': courses
    })

# Library view
def library_view(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        borrowed_books = student.borrowed_books.all()
        books = Library.objects.all()
        return render(request, 'student/library/library.html', {
            'student': student,
            'borrowed_books': borrowed_books,
            'books': books,
        })
    except Student.DoesNotExist:
        messages.error(request, "Student not found!")
        return redirect('home')

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
grading_queue = GradingQueue()

def student_dashboard(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    courses = student.enrolled_courses.all()
    attendance = student.attendances.all()
    
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
        'attendance': attendance,
        'schedules': today_schedules,
    }

    return render(request, 'student/student_dashboard.html', context)

# Course detail view
def course_detail(request, student_id, course_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)
    materials = course.materials.all().order_by('-upload_date')
    assignments = course.assignments.all().order_by('due_date')

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        submission_file = request.FILES.get('submission_file')
        
        if assignment_id and submission_file:
            assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
            
            # Create submission
            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                file=submission_file
            )
            messages.success(request, 'Assignment submitted successfully!')
            
    return render(request, 'student/course/course_detail.html', {
        'student': student,
        'course': course,
        'materials': materials,
        'assignments': assignments
    })

# Course materials
def course_materials(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    materials = course.materials.all()

    return render(request, 'course_materials.html', {'student': student, 'course': course, 'materials': materials})

# Course schedule
def course_schedule(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    schedules = Schedule.objects.filter(course=course)

    return render(request, 'course_schedule.html', {'student': student, 'course': course, 'schedules': schedules})

# Assignment detail
def assignment_detail(request, student_id, course_id, assignment_id):
    student = get_object_or_404(Student, pk=student_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()

    if request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = student
            submission.save()
            grading_queue.enqueue(submission)
            messages.success(request, "Assignment submitted successfully.")
            return redirect('assignment_detail', student_id=student.id, course_id=course_id, assignment_id=assignment.id)

    else:
        form = AssignmentSubmissionForm()

    return render(request, 'assignment_detail.html', {
        'student': student,
        'assignment': assignment,
        'submissions': submissions,
        'form': form
    })

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
    material = get_object_or_404(CourseMaterial, material_id=material_id, course__professor=professor)
    
    material.file.delete()  # Delete the actual file
    material.delete()       # Delete the database record
    messages.success(request, 'Material deleted successfully')
    
    return redirect('course_materials_manage', professor_id=professor_id, course_id=course_id)

def update_course_material(request, professor_id, course_id, material_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    material = get_object_or_404(CourseMaterial, material_id=material_id, course__professor=professor)
    
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

    return render(request, 'professor/update_material.html', {
        'professor': professor,
        'course': material.course,
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

def add_assignment(request, professor_id, course_id):
    if request.method == 'POST':
        professor = get_object_or_404(Professor, professor_id=professor_id)
        course = get_object_or_404(Course, course_id=course_id)
        
        try:
            Assignment.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                due_date=request.POST['due_date'],
                course=course
            )
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

def grade_submissions(request, professor_id, course_id, assignment_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    
    if request.method == 'POST':
        grades = request.POST.getlist('grades[]')
        for submission_id, grade in grades.items():
            submission = get_object_or_404(AssignmentSubmission, submission_id=submission_id)
            submission.grade = grade
            submission.save()
        messages.success(request, 'Grades saved successfully')
        return redirect('manage_assignments', professor_id=professor_id, course_id=course_id)
    
    return render(request, 'professor/assignments/grade.html', {
        'professor': professor,
        'course': course,
        'assignment': assignment,
        'submissions': submissions
    })

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
    if request.method == 'POST':
        try:
            for key, grade in request.POST.items():
                if key.startswith('grade_'):
                    submission_id = key.replace('grade_', '')
                    submission = AssignmentSubmission.objects.get(submission_id=submission_id)
                    submission.grade = grade
                    submission.save()
            messages.success(request, 'Grades saved successfully')
        except Exception as e:
            messages.error(request, f'Error saving grades: {str(e)}')
    
    return redirect('grade_submissions', professor_id=professor_id, 
                   course_id=course_id, assignment_id=assignment_id)

class AssignmentSubmissionFactory:
    @staticmethod
    def create_submission(assignment, student, file):
        return AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student,
            file=file
        )

def submit_assignment(request, student_id, course_id, assignment_id):
    if request.method == 'POST':
        try:
            student = get_object_or_404(Student, pk=student_id)
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            submission_file = request.FILES.get('submission_file')
            
            if submission_file:
                # Check if submission already exists
                existing_submission = AssignmentSubmission.objects.filter(
                    assignment=assignment,
                    student=student
                ).first()
                
                if existing_submission:
                    return JsonResponse({
                        'success': False, 
                        'error': 'You have already submitted this assignment'
                    })
                
                # Create new submission using factory
                submission = AssignmentSubmissionFactory.create_submission(
                    assignment=assignment,
                    student=student,
                    file=submission_file
                )
                # Enqueue the submission
                grading_queue.append(submission)
    
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'No file uploaded'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def manage_assignments(request, professor_id, course_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)
    assignments = Assignment.objects.filter(course=course).order_by('due_date')

    return render(request, 'professor/assignments/manage.html', {
        'professor': professor,
        'course': course,
        'assignments': assignments
    })

def add_schedule(request, professor_id, course_id):
    professor = get_object_or_404(Professor, professor_id=professor_id)
    course = get_object_or_404(Course, course_id=course_id)

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        room = request.POST.get('room')

        try:
            Schedule.objects.create(
                course=course,
                date=date,
                time=time,
                room=room
            )
            messages.success(request, 'Schedule added successfully')
        except Exception as e:
            messages.error(request, f'Error adding schedule: {str(e)}')

        return redirect('course_schedule', student_id=professor_id, course_id=course_id)

    return render(request, 'professor/schedule/add.html', {
        'professor': professor,
        'course': course
    })
