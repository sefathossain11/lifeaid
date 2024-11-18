# forms.py

from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

from .models import Patient, User  # Ensure correct import based on your project structure


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. 5-30 characters. Letters, numbers, and underscores only.',
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )

    class Meta:
        model = User
        # Include other fields as necessary
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Define the desired username pattern
        # - Must start with a letter
        # - Can contain letters, numbers, and underscores
        # - Length between 5 to 30 characters
        pattern = r'^[A-Za-z][A-Za-z0-9_]{4,29}$'

        if not re.match(pattern, username):
            raise ValidationError(
                "Invalid username. It must start with a letter and contain only letters, numbers, and underscores. Length between 5-30 characters."
            )

        # Check for username uniqueness (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Username already exists. Please choose a different one.")

        return username


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'phone_number', 'blood_group',
                  'featured_image', 'history', 'nid', 'dob', 'address']

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class PasswordResetForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})
