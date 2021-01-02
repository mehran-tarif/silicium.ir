from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
	email = models.EmailField(unique=True, verbose_name='آدرس ایمیل')

	class Meta:
		verbose_name = "کاربر"
		verbose_name_plural = "کاربران"
		ordering = ['-is_superuser']