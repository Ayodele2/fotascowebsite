from typing import Any
from django import forms
from .models import UserRegistration
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserRegistration
        fields = [
            'full_name', 'dob', 'email', 'phone', 'gender', 'roles', 
            'account_name', 'account_number', 'bank_name', 'address', 
            'next_of_kin', 'relationship'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def clean(self):
        clean_data =  super().clean()
        email = clean_data.get("email")
        phone = clean_data.get("phone")
        if UserRegistration.objects.filter(email=email).exists():
            self.add_error('email', "Email already exists.")
            raise ValidationError("Email already in used")
        if UserRegistration.objects.filter(phone=phone).exists():
            self.add_error('phone', "Phone number already exists.")
            raise ValidationError("Phone already exist")
        
        return clean_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
