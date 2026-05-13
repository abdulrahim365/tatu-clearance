from django import forms
from .models import ClearanceRequest

class ClearanceApplicationForm(forms.ModelForm):
    class Meta:
        model = ClearanceRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }