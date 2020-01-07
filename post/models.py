# Different types of posts

from django.contrib.auth import get_user_model
from django.db import models
import time


# Text Post
class Post(models.Model):
    author = models.ForeignKey(
        get_user_model(), 
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=120)
    description = models.TextField()
    body = models.TextField()
    completed = models.BooleanField(default=False)

    def _str_(self):
        return self.title


# Image Post
class IPost(Post):
    image = models.ImageField(
                upload_to=None, 
                height_field=None, 
                width_field=None, 
                max_length=100
            )


# Video Post
class VPost(Post):
    video = models.FileField(
                upload_to=None,
                blank=True,
                null=True
            )
