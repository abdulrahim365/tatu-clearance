from django.contrib import admin

# Register your models here.
# accounts/admin.py
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, ApproverProfile

# Register the custom User model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone')}),
    )

# Register Student Profile
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'programme', 'department', 'level')
    search_fields = ('student_id', 'user__username', 'programme')
    list_filter = ('department', 'level')

# Register Approver Profile
@admin.register(ApproverProfile)
class ApproverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'unit')
    search_fields = ('user__username', 'unit__name')