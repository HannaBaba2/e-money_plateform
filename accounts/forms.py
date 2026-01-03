# accounts/forms.py
from django import forms
from django.contrib.auth import password_validation
from .models import User

class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html()
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned