from django.contrib import admin
from .models import (
    Student,
    Professor,
    Staff,
    Library,
    Room,
    Department,
    Course,
    Schedule,
    Assignment,
    Attendance,
    Enrollment,
)

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1

# Admin Configuration
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'student_id', 'get_enrolled_courses')
    search_fields = ('name', 'email', 'student_id')
    exclude = ('student_id', 'last_login')
    inlines = [EnrollmentInline]

    def get_enrolled_courses(self, obj):
        return ", ".join(course.name for course in obj.enrolled_courses.all())
    get_enrolled_courses.short_description = 'Enrolled Courses'

    
@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'professor_id', 'department')
    search_fields = ('name', 'email', 'professor_id')
    list_filter = ('department',)
    exclude = ('professor_id',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'staff_id', 'position', 'department')
    search_fields = ('name', 'email', 'staff_id', 'position')
    list_filter = ('department',)
    exclude = ('staff_id',)


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'category', 'quantity', 'status')
    search_fields = ('book_name', 'category')
    list_filter = ('status',)
    exclude = ('book_id',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'capacity', 'department')
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
    list_display = ('course_id', 'name')
    search_fields = ('course_id', 'name')
    exclude = ('course_id',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'time', 'type', 'room')
    search_fields = ('course__name', 'type')
    list_filter = ('type',)
    exclude = ('schedule_id',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'grade')
    search_fields = ('title', 'course__name')
    list_filter = ('due_date',)
    exclude = ('assignment_id',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'attendance_percent')
    search_fields = ('student__name', 'course__name')
    list_filter = ('attendance_percent',)
    exclude = ('attendance_id',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date')
    search_fields = ('student__name', 'course__name')
    list_filter = ('enrollment_date',)
    exclude = ('enrollment_id',)
