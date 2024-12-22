# file: views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import (
    Student, Professor, Course, Library, BorrowQueue, Schedule,
    Assignment, AssignmentSubmission, GradingQueue, BookLending
)
from .forms import AssignmentSubmissionForm
from django.contrib import messages
from django.utils import timezone

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
            return redirect('professor_dashboard', professor_id=professor.id)

        # Invalid credentials
        messages.error(request, "Invalid email or password.")
        return redirect('login')

    return render(request, 'login.html')

# Professor dashboard
def professor_dashboard(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    return render(request, 'professor_dashboard.html', {'professor': professor})

# Library view
borrow_queue = BorrowQueue()

def library_view(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        borrowed_books = student.borrowed_books.all()
        books = Library.objects.all()
        return render(request, 'library.html', {
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
    schedules = Schedule.objects.filter(course__in=courses)

    return render(request, 'student_dashboard.html', {
        'student': student,
        'courses': courses,
        'attendance': attendance,
        'schedules': schedules
    })

# Course detail view
def course_detail(request, student_id, course_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'course_detail.html', {'student': student, 'course': course})

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
