from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('approver', 'Approver'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class StudentProfile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, help_text="e.g. 20230001")
    programme = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    level = models.CharField(max_length=10, default="HND 4")   # or BTech etc.

    def __str__(self):
        return self.student_id

class ApproverProfile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='approver_profile')
    unit = models.ForeignKey('clearance.Unit', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.unit.name}"
