from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import ads as ad_models
from core.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (("Дополнительная информация", {"fields": ("position", "phone_number")}),)

    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Дополнительно", {"fields": ("position", "phone_number")}),)

    list_display = ("username", "email", "first_name", "last_name", "position", "is_staff")


@admin.register(ad_models.Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user__username",
        "start_date",
        "end_date",
    )
    search_fields = ("name",)


@admin.register(ad_models.Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "campaign__name",
        "place",
    )
    search_fields = ("name",)


@admin.register(ad_models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "advertisement__name",
        "uid",
        "is_active",
    )
    search_fields = ("uid",)
