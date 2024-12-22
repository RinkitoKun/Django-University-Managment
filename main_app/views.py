from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import Student, Professor, Course, Library, BorrowRequestQueue, Schedule, Assignment, AssignmentSubmission, GradingQueue
from .forms import AssignmentSubmissionForm




def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Check if the user is a Student
        student = Student.objects.filter(email=email).first()
        if student and student.password == password:
            # Redirect to Student Dashboard
            return redirect('student_dashboard', student_id=student.student_id)
        
        # Check if the user is a Professor
        professor = Professor.objects.filter(email=email).first()
        if professor and professor.password == password:
            # Redirect to Professor Dashboard
            return redirect('professor_dashboard', professor_id=professor.id)
        
        # Invalid credentials
        return render(request, 'login.html', {'error': 'Invalid email or password'})
    
    return render(request, 'login.html')





def professor_dashboard(request, professor_id):
    professor = Professor.objects.get(id=professor_id)
    return render(request, 'professor_dashboard.html', {'professor': professor})

borrow_queue = BorrowRequestQueue()

def library_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    books = list(Library.objects.all())

    # Apply quick sort algorithm to sort books alphabetically by name
    def quick_sort_books(books):
        if len(books) <= 1:
            return books
        pivot = books[0]
        lesser = [book for book in books[1:] if book.book_name < pivot.book_name]
        greater = [book for book in books[1:] if book.book_name >= pivot.book_name]
        return quick_sort_books(lesser) + [pivot] + quick_sort_books(greater)

    sorted_books = quick_sort_books(books)
    return render(request, 'library.html', {'student': student, 'books': sorted_books})


def borrow_book(request, student_id, book_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        book = get_object_or_404(Library, id=book_id)

        if book.status == 'Present':
            book.status = 'Borrowed'
            book.borrower = student
            book.save()
    return redirect('library', student_id=student_id)


def return_book(request, student_id, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Library, id=book_id)

        if book.status == 'Borrowed':
            book.status = 'Present'
            book.borrower = None
            book.save()
    return redirect('library', student_id=student_id)


grading_queue = GradingQueue()

def student_dashboard(request,student_id):
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

def course_detail(request, student_id, course_id, assignment_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)
    assignment=get_object_or_404(Assignment,pk=assignment_id)
    return render(request, 'course_detail.html', {'student': student, 'course': course, 'assignment': assignment})


def course_materials(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    materials = course.materials.all()

    return render(request, 'course_materials.html', {'student': student, 'course': course, 'materials': materials})


def course_schedule(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    schedules = Schedule.objects.filter(course=course)

    return render(request, 'course_schedule.html', {'student': student, 'course': course, 'schedules': schedules})


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
            return redirect('assignment_detail', student_id=student.id, course_id=course_id, assignment_id=assignment.id)

    else:
        form = AssignmentSubmissionForm()

    return render(request, 'assignment_detail.html', {
        'student': student,
        'assignment': assignment,
        'submissions': submissions,
        'form': form
    })