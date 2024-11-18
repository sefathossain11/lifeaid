# forms.py

from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

from hospital.models import User  # Ensure correct import based on your project structure
from .models import Doctor_Information  # Ensure correct import based on your project structure


class DoctorUserCreationForm(UserCreationForm):
    """
    Custom form for creating new doctor users with enhanced username validation.
    Inherits from Django's UserCreationForm.
    """

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
        fields = ['username', 'email', 'password1', 'password2']
        # You can uncomment and customize labels if needed
        # labels = {
        #     'username': 'Username',
        #     'email': 'Email Address',
        #     'password1': 'Password',
        #     'password2': 'Confirm Password',
        # }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and add CSS classes to form fields for styling.
        """
        super(DoctorUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})

    def clean_username(self):
        """
        Validate the username to ensure it starts with a letter, contains only letters, numbers, and underscores,
        and is between 5 to 30 characters long. Also, ensure the username is unique (case-insensitive).
        """
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


class DoctorForm(ModelForm):
    """
    Form for handling additional doctor-specific information.
    Inherits from Django's ModelForm.
    """

    class Meta:
        model = Doctor_Information
        fields = [
            'name', 'email', 'phone_number', 'degree', 'department',
            'featured_image', 'visiting_hour', 'consultation_fee',
            'report_fee', 'dob', 'hospital_name'
        ]
        # You can customize widgets or labels if needed
        # widgets = {
        #     'name': forms.TextInput(attrs={'class': 'form-control'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control'}),
        #     # Add other fields as necessary
        # }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and add CSS classes to form fields for styling.
        """
        super(DoctorForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
