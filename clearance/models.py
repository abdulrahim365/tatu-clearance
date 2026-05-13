from django.db import models

# Create your models here.

from django.db import models
from django.utils import timezone
from accounts.models import User

class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']

class ClearanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clearance_requests')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Clearance - {self.student.student_profile.student_id}"

    @property
    def is_complete(self):
        return all(step.status == 'approved' for step in self.steps.all())

class ClearanceStep(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    request = models.ForeignKey(ClearanceRequest, on_delete=models.CASCADE, related_name='steps')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('request', 'unit')

    def __str__(self):
        return f"{self.request} - {self.unit.name} ({self.status})"
