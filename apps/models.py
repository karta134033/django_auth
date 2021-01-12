from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

class CustomUser(AbstractBaseUser, models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    update_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'custom_user'
        constraints = [
            models.UniqueConstraint(
                fields=['username'], name='unique_username')
        ]