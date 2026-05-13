from weakref import ref

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import HttpResponse
from matplotlib.pyplot import step
from weasyprint import HTML

from .models import ClearanceRequest, ClearanceStep, Unit
from .forms import ClearanceApplicationForm
from accounts.models import StudentProfile, ApproverProfile

@login_required
def approve_step(request, step_id):
    """Approver reviews and approves/rejects a step"""
    step = get_object_or_404(ClearanceStep, id=step_id)

    # Security check
    if request.user.role != 'approver' or step.unit != request.user.approver_profile.unit:
        messages.error(request, "You are not authorized to approve this step.")
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '').strip()

        step.comment = comment
        step.approver = request.user
        step.approved_date = timezone.now()

        if action == 'approve':
            step.status = 'approved'
            messages.success(request, f"✅ Approved: {step.request.student.student_profile.student_id}")
        else:
            step.status = 'rejected'
            messages.warning(request, f"❌ Rejected: {step.request.student.student_profile.student_id}")

        step.save()

        # Update parent request status
        req = step.request
        if req.is_complete:
            req.status = 'approved'
            req.completed_date = timezone.now()
            req.save()

        # === Send Email Notification ===
        try:
            if step.status == 'approved':
                subject = f"✅ Clearance Step Approved - {step.unit.name}"
            else:
                subject = f"❌ Clearance Step Rejected - {step.unit.name}"

            html_message = render_to_string('clearance/email_step_update.html', {
                'step': step,
                'student': req.student,
                'completed': req.steps.filter(status='approved').count()
            })

            send_mail(
                subject=subject,
                message="Your clearance request has been updated.",  # Plain text version
                from_email=None,
                recipient_list=[req.student.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")  # For debugging

        return redirect('dashboard')

    return render(request, 'clearance/approve.html', {'step': step})


@login_required
def dashboard(request):
    if request.user.role == 'student':
        requests = ClearanceRequest.objects.filter(student=request.user).order_by('-applied_date')
        
        # Calculate counts in the view (safe way)
        completed = 0
        for req in requests:
            if req.is_complete:
                completed += 1

        return render(request, 'clearance/student_dashboard.html', {
            'requests': requests,
            'completed_count': completed,
        })

    elif request.user.role == 'approver':
        profile = get_object_or_404(ApproverProfile, user=request.user)
        pending_steps = ClearanceStep.objects.filter(
            unit=profile.unit, 
            status='pending'
        ).select_related('request__student__student_profile')
        
        return render(request, 'clearance/approver_dashboard.html', {
            'pending_steps': pending_steps,
            'unit': profile.unit
        })

    else:  # Admin
        total = ClearanceRequest.objects.count()
        approved = ClearanceRequest.objects.filter(status='approved').count()
        return render(request, 'clearance/admin_dashboard.html', {
            'total_requests': total,
            'approved': approved,
            'pending': total - approved,
        })


@login_required
def apply_clearance(request):
    """Student applies for clearance"""
    if request.user.role != 'student':
        messages.error(request, "Only students can apply for clearance.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClearanceApplicationForm(request.POST)
        if form.is_valid():
            clearance = form.save(commit=False)
            clearance.student = request.user
            clearance.save()

            # Auto-create one step for every unit
            units = Unit.objects.all()
            for unit in units:
                ClearanceStep.objects.create(request=clearance, unit=unit)

            messages.success(request, "Your clearance application has been submitted successfully!")
            return redirect('dashboard')
    else:
        form = ClearanceApplicationForm()

    return render(request, 'clearance/apply.html', {'form': form})


@login_required
def approve_step(request, step_id):
    """Approver reviews and approves/rejects a step"""
    step = get_object_or_404(ClearanceStep, id=step_id)

    # Security check
    if request.user.role != 'approver' or step.unit != request.user.approver_profile.unit:
        messages.error(request, "You are not authorized to approve this step.")
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '').strip()

        step.comment = comment
        step.approver = request.user
        step.approved_date = timezone.now()

        if action == 'approve':
            step.status = 'approved'
            messages.success(request, f"✅ Approved for {step.request.student.student_profile.student_id}")
        else:
            step.status = 'rejected'
            messages.warning(request, f"❌ Rejected for {step.request.student.student_id}")

        step.save()

        # Update parent request
        req = step.request

        # Check if all steps are now approved
        if req.is_complete and req.status != 'approved':
            req.status = 'approved'
            req.completed_date = timezone.now()
            req.save()

            # Send Completion Email
            try:
                html_message = render_to_string('clearance/email_clearance_complete.html', {
                    'student': req.student,
                })
                send_mail(
                    subject="🎉 Congratulations! Your Clearance is Complete",
                    message="Your clearance has been fully approved.",
                    from_email=None,
                    recipient_list=[req.student.email],
                    html_message=html_message,
                )
            except Exception as e:
                print(f"Completion email failed: {e}")

        else:
            # Send normal step update email
            try:
                if step.status == 'approved':
                    subject = f"✅ Clearance Step Approved - {step.unit.name}"
                else:
                    subject = f"❌ Clearance Step Rejected - {step.unit.name}"

                html_message = render_to_string('clearance/email_step_update.html', {
                    'step': step,
                    'student': req.student,
                    'completed': req.steps.filter(status='approved').count()
                })

                send_mail(
                    subject=subject,
                    message="Your clearance request has been updated.",
                    from_email=None,
                    recipient_list=[req.student.email],
                    html_message=html_message,
                )
            except Exception as e:
                print(f"Step update email failed: {e}")

        return redirect('dashboard')

    return render(request, 'clearance/approve.html', {'step': step})

@login_required
def download_certificate(request, request_id):
    """Generate and download official TaTu PDF clearance certificate"""
    clearance = get_object_or_404(ClearanceRequest, id=request_id, student=request.user)

    if not clearance.is_complete:
        messages.error(request, "Your clearance is not yet complete. All units must approve first.")
        return redirect('dashboard')

    # Render certificate template
    html_string = render_to_string('clearance/certificate.html', {
        'clearance': clearance,
        'student': clearance.student.student_profile
    })

    # Generate PDF
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TaTu_Clearance_{clearance.student.student_profile.student_id}.pdf"'
    return response
   


# ====================== In apply_clearance function ======================
@login_required
def apply_clearance(request):
    if request.user.role != 'student':
        messages.error(request, "Only students can apply for clearance.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClearanceApplicationForm(request.POST)
        if form.is_valid():
            clearance = form.save(commit=False)
            clearance.student = request.user
            clearance.save()

            # Create steps
            units = Unit.objects.all()
            for unit in units:
                ClearanceStep.objects.create(request=clearance, unit=unit)

            # Send email notification to student
            try:
                html_message = render_to_string('clearance/email_new_request.html', {
                    'student': request.user,
                    'request': clearance
                })
                send_mail(
                    subject="✅ Your Clearance Request Has Been Submitted",
                    message="Your clearance request was received.",
                    from_email=None,
                    recipient_list=[request.user.email],
                    html_message=html_message,
                )
            except:
                pass  # Fail silently in development

            messages.success(request, "Your clearance application has been submitted successfully!")
            return redirect('dashboard')
    else:
        form = ClearanceApplicationForm()

    return render(request, 'clearance/apply.html', {'form': form})

    
