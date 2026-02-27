from django.shortcuts import get_object_or_404
from rest_framework import generics

from api import serializers
from api.pagination import CampaignPagination
from core.models import ads as ads_models


class CampaignListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.CampaignSerializer
    pagination_class = CampaignPagination

    def get_queryset(self):
        return ads_models.Campaign.objects.filter(user=self.request.user)  # TODO: LOGIC-4, DJANGO-7

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CampaignSerializer

    def get_queryset(self):
        return ads_models.Campaign.objects.filter(user=self.request.user)


class AdvertisementListCreateView(generics.ListCreateAPIView):  # TODO: LOGIC-5
    serializer_class = serializers.AdvertisementSerializer

    def get_campaign(self):  # TODO: DJANGO-6
        return get_object_or_404(ads_models.Campaign, id=self.kwargs["campaign_id"], user=self.request.user)

    def get_queryset(self):
        campaign = self.get_campaign()
        return ads_models.Advertisement.objects.filter(campaign=campaign)

    def perform_create(self, serializer):
        campaign = self.get_campaign()
        serializer.save(campaign=campaign)


class AdvertisementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.AdvertisementSerializer

    def get_queryset(self):
        return ads_models.Advertisement.objects.filter(
            campaign__id=self.kwargs["campaign_id"], campaign__user=self.request.user
        )


class BannerListCreateView(generics.ListCreateAPIView):  # TODO: LOGIC-5
    serializer_class = serializers.BannerSerializer

    def get_advertisement(self):  # TODO: DJANGO-6
        return get_object_or_404(ads_models.Advertisement, id=self.kwargs["ad_id"], campaign__user=self.request.user)

    def get_queryset(self):
        ad = self.get_advertisement()
        return ads_models.Banner.objects.filter(advertisement=ad)

    def perform_create(self, serializer):
        ad = self.get_advertisement()
        serializer.save(advertisement=ad)


class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):  # TODO: LOGIC-3
    serializer_class = serializers.BannerSerializer

    def get_queryset(self):
        return ads_models.Banner.objects.filter(
            advertisement__id=self.kwargs["ad_id"], advertisement__campaign__user=self.request.user
        )
