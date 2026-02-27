from django.urls import path

from . import views as api_view

app_name = "api"

urlpatterns = [
    path("campaigns", api_view.CampaignListCreateView.as_view(), name="campaigns"),
    path("campaigns/<int:pk>", api_view.CampaignDetailView.as_view(), name="campaign_detail"),
    path("campaigns/<int:campaign_id>/ads", api_view.AdvertisementListCreateView.as_view(), name="ads"),
    path("campaigns/<int:campaign_id>/ads/<int:pk>", api_view.AdvertisementDetailView.as_view(), name="ad_detail"),
    path("ads/<int:ad_id>/banners", api_view.BannerListCreateView.as_view(), name="banners"),
    path("ads/<int:ad_id>/banners/<int:pk>", api_view.BannerDetailView.as_view(), name="banner_detail"),
]
