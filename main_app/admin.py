from django.contrib import admin
from .models import (
    Student, Professor, Staff, Course, Library, Schedule,
    Assignment, AssignmentSubmission, Room, Department, Attendance,
    Enrollment, CourseMaterial, BookLending
)

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1

class ProfessorCoursesInline(admin.TabularInline):
    model = Professor.courses.through
    extra = 1
    verbose_name = "Course"
    verbose_name_plural = "Courses"

# Admin Configuration
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'student_id', 'get_enrolled_courses')
    search_fields = ('name', 'email', 'student_id')
    inlines = [EnrollmentInline]

    def get_enrolled_courses(self, obj):
        return ", ".join(course.name for course in obj.enrolled_courses.all())
    get_enrolled_courses.short_description = 'Enrolled Courses'

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'professor_id', 'department', 'get_courses')
    search_fields = ('name', 'email', 'professor_id')
    exclude = ('staff_id', 'student_id', 'courses')  # Exclude courses field since we're using inline
    inlines = [ProfessorCoursesInline]

    def get_courses(self, obj):
        return ", ".join([course.name for course in obj.courses.all()])
    get_courses.short_description = 'Courses'

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'staff_id', 'position', 'department')
    search_fields = ('name', 'email', 'staff_id', 'position')
    list_filter = ('department',)
    exclude = ('staff_id',)

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'book_name', 'category', 'quantity', 'status')
    search_fields = ('book_name', 'category', 'book_id')
    list_filter = ('status', 'category')
    readonly_fields = ('book_id',)

@admin.register(BookLending)
class BookLendingAdmin(admin.ModelAdmin):
    list_display = ('book', 'student', 'borrow_date', 'return_date')
    list_filter = ('borrow_date', 'return_date')
    search_fields = ('book__book_name', 'student__name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'room_type', 'department')
    search_fields = ('room_type',)
    list_filter = ('department',)
    exclude = ('room_id',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)
    exclude = ('department_id',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'get_professors')
    search_fields = ('course_id', 'name')

    def get_professors(self, obj):
        return ", ".join([prof.name for prof in obj.professors.all()])
    get_professors.short_description = 'Professors'

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'time', 'type', 'room')
    search_fields = ('course__name', 'type')
    list_filter = ('type',)
    exclude = ('schedule_id',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'title', 'due_date', 'course')
    search_fields = ('title', 'course__name')
    list_filter = ('course', 'due_date')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'student', 'assignment', 'submission_date', 'grade')
    search_fields = ('student__name', 'assignment__title')
    list_filter = ('submission_date', 'grade')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'is_present', 'attendance_percent')
    search_fields = ('student__name', 'course__name')
    list_filter = ('is_present', 'course')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date')
    search_fields = ('student__name', 'course__name')
    list_filter = ('enrollment_date',)

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'title', 'course', 'upload_date')
    search_fields = ('title', 'course__name')
    list_filter = ('course', 'upload_date')
