# Types of users

from django.db import models
from django.contrib.auth.models import AbstractUser
import time


class BaseUser(AbstractUser):
	pass

	def __str__(self):
		return self.username

