# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create StudentProfile when a new student user is created"""
    if created and instance.role == 'student':
        StudentProfile.objects.create(
            user=instance,
            student_id=f"TATU{instance.date_joined.strftime('%Y%m%d')}{str(instance.id).zfill(4)}",
            programme="HND Computer Science",   # Default value - you can change later
            department="Computer Science",
            level="HND 4"
        )
        print(f"✅ StudentProfile auto-created for {instance.username}")