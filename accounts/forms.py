from django import forms
from django.contrib.auth import password_validation
from .models import User, Gender

class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label= "Nom (optionnel)"
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Prénom"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Mot de passe",
        help_text=password_validation.password_validators_help_text_html()
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmer le mot de passe"
    )
    gender = forms.ChoiceField(
        choices=Gender.choices,
        label="Genre",
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'gender',
            'password'
        ]
        labels = {
            'username': "Nom d'utilisateur",
            'email': "Adresse e-mail",
            'phone_number': "Numéro de téléphone (8 chiffres)",
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data