from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "is_active",
            "is_superuser",
            "is_staff",
            "setor",
        ]