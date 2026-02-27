import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

ALLOWED_EXTENSIONS = ["gif", "png", "jpg", "jpeg", "htm", "html"]


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Campaign(TimeStampModel):
    class SpendingStrategy(models.TextChoices):
        MAX_IMPRESSIONS = "max_impressions", "Максимальные показы"
        EVENLY = "evenly", "Равномерное распределение бюджета"

    name = models.CharField(max_length=255, verbose_name="Название кампании")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns", db_index=True)
    start_date = models.DateField(verbose_name="Дата старта", db_index=True)
    end_date = models.DateField(verbose_name="Дата завершения", db_index=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Бюджет")
    strategy = models.CharField(max_length=31, choices=SpendingStrategy.choices, verbose_name="Стратегия трат")
    max_impressions_per_day = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        verbose_name="максимальное число показов в день",
    )
    targeting = models.JSONField(default=dict, blank=True, verbose_name="Таргетинг")

    class Meta:
        verbose_name = "Рекламная кампания"
        verbose_name_plural = "Рекламные кампании"
        constraints = [
            models.CheckConstraint(check=Q(budget__gte=0), name="budget_positive"),
            models.CheckConstraint(
                check=(
                    Q(strategy="max_impressions", max_impressions_per_day__isnull=False)
                    | Q(strategy="evenly", max_impressions_per_day__isnull=True)
                ),
                name="strategy_impressions_constraint",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала")

        if self.strategy == self.SpendingStrategy.MAX_IMPRESSIONS:
            if self.max_impressions_per_day is None:
                raise ValidationError("Для стратегии 'максимальные показы' нужно указать max_impressions_per_day")
        else:
            if self.max_impressions_per_day is not None:
                raise ValidationError("max_impressions_per_day используется только для стратегии 'максимальные показы'")


class Advertisement(TimeStampModel):
    class Placement(models.TextChoices):
        SITE = "site", "Сайт"
        MOBILE_APP = "mobile_app", "Мобильное приложение"
        STORE_SCREEN = "store_screen", "Экран в магазине"

    name = models.CharField(max_length=255, verbose_name="Название объявления")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="advertisements", verbose_name="Кампания")
    place = models.CharField(max_length=20, choices=Placement.choices, verbose_name="Место размежения")
    url = models.URLField(verbose_name="Url рекламного объекта")
    description = models.TextField(verbose_name="Текст объявления")

    class Meta:
        verbose_name = "Рекламное объявление"
        verbose_name_plural = "Рекламные объявления"

    def __str__(self):
        return self.name


def banner_upload_path(instance, filename: str):
    ext = filename.split(".")[-1].lower()
    return f"banners/{instance.advertisement_id}/{instance.uid}/{uuid.uuid4()}.{ext}"


class Banner(TimeStampModel):
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, related_name="banners", verbose_name="Объявление"
    )
    uid = models.CharField(max_length=255, verbose_name="Внешний сквозной идентификатор", unique=True)
    width = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], verbose_name="Ширина")
    height = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], verbose_name="Высота")
    file = models.FileField(
        upload_to=banner_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        verbose_name="Файл с рекламными материалами",
    )
    is_active = models.BooleanField(default=True, verbose_name="Статус", db_index=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return f"{self.uid} ({self.width}x{self.height})"
