from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import BaseUserCreationForm, BaseUserChangeForm
from .models import BaseUser


class UsersAdmin(UserAdmin):
	add_form = BaseUserCreationForm
	form = BaseUserChangeForm
	model = BaseUser
	list_display = ('username', 'email')


admin.site.register(BaseUser, UsersAdmin)
