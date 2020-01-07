from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import BaseUser


class BaseUserCreationForm(UserCreationForm):
    class Meta:
        model = BaseUser
        fields = ('username', 'email')


class BaseUserChangeForm(UserChangeForm):
    class Meta:
        model = BaseUser
        fields = ('username', 'email')
