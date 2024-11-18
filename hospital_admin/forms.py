# forms.py

from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

from hospital.models import User, Hospital_Information
from .models import Admin_Information, Clinical_Laboratory_Technician

# ----------------------------
# 1. Username Validation Mixin
# ----------------------------

class UsernameValidationMixin:
    """
    Mixin to add username validation to UserCreationForms.
    Ensures that the username:
    - Starts with a letter.
    - Contains only letters, numbers, and underscores.
    - Is between 5 to 30 characters long.
    - Is unique (case-insensitive).
    """
    
    def clean_username(self):
        """
        Validates the username field according to the specified criteria.
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

# ---------------------------------
# 2. User Creation Forms with Mixin
# ---------------------------------

class AdminUserCreationForm(UsernameValidationMixin, UserCreationForm):
    """
    Custom form for creating new admin users with enhanced username validation.
    Inherits from UsernameValidationMixin and Django's UserCreationForm.
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
        # Uncomment and customize labels if needed
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
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class LabWorkerCreationForm(UsernameValidationMixin, UserCreationForm):
    """
    Custom form for creating new clinical laboratory technician users with enhanced username validation.
    Inherits from UsernameValidationMixin and Django's UserCreationForm.
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
        # Uncomment and customize labels if needed
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
        super(LabWorkerCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class PharmacistCreationForm(UsernameValidationMixin, UserCreationForm):
    """
    Custom form for creating new pharmacist users with enhanced username validation.
    Inherits from UsernameValidationMixin and Django's UserCreationForm.
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
        # Uncomment and customize labels if needed
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
        super(PharmacistCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

# ---------------------------------
# 3. Other Forms Without Username Validation
# ---------------------------------

class AddHospitalForm(ModelForm):
    """
    Form for adding a new hospital.
    Inherits from Django's ModelForm.
    """
    
    class Meta:
        model = Hospital_Information
        fields = ['name', 'address', 'featured_image', 'phone_number', 'email', 'hospital_type']

    def __init__(self, *args, **kwargs):
        super(AddHospitalForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class EditHospitalForm(ModelForm):
    """
    Form for editing existing hospital information.
    Inherits from Django's ModelForm.
    """
    
    class Meta:
        model = Hospital_Information
        fields = ['name', 'address', 'featured_image', 'phone_number', 'email', 'hospital_type']

    def __init__(self, *args, **kwargs):
        super(EditHospitalForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class EditEmergencyForm(ModelForm):
    """
    Form for editing hospital emergency details.
    Inherits from Django's ModelForm.
    """
    
    class Meta:
        model = Hospital_Information
        fields = ['general_bed_no', 'available_icu_no', 'regular_cabin_no', 'emergency_cabin_no', 'vip_cabin_no']

    def __init__(self, *args, **kwargs):
        super(EditEmergencyForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class AddEmergencyForm(ModelForm):
    """
    Form for adding emergency details to a hospital.
    Inherits from Django's ModelForm.
    """
    
    class Meta:
        model = Hospital_Information
        fields = ['name', 'general_bed_no', 'available_icu_no', 'regular_cabin_no', 'emergency_cabin_no', 'vip_cabin_no']

    def __init__(self, *args, **kwargs):
        super(AddEmergencyForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class AdminForm(ModelForm):
    """
    Form for editing admin information.
    Inherits from Django's ModelForm.
    """
    
    class Meta:
        model = Admin_Information
        fields = ['name', 'email', 'phone_number', 'role', 'featured_image']

    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
