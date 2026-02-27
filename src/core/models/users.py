from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    position = models.CharField(max_length=255, verbose_name="Должность")
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(regex=r"^\+?\d{10,15}$", message="Телефон должен быть в формате +71234567890")],
        verbose_name="Телефон",
    )

    def __str__(self):
        return f"{self.username} ({self.position})"
