from django import forms

from core.models import ads as ad_models


class CampaignForm(forms.ModelForm):
    class Meta:
        model = ad_models.Campaign
        exclude = ("user",)  # TODO: DJANGO-4


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = ad_models.Advertisement
        exclude = ("campaign",)  # TODO: DJANGO-4


class BannerForm(forms.ModelForm):
    class Meta:
        model = ad_models.Banner
        exclude = ("advertisement",)  # TODO: DJANGO-4
