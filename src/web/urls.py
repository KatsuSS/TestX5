from django.urls import path

from . import views as web_view

app_name = "web"

urlpatterns = [
    path("", web_view.CampaignListView.as_view(), name="campaign-list"),
    path("create/", web_view.CampaignCreateView.as_view(), name="campaign-create"),
    path("<int:pk>/edit/", web_view.CampaignUpdateView.as_view(), name="campaign-edit"),
    path("<int:pk>/delete/", web_view.CampaignDeleteView.as_view(), name="campaign-delete"),
    path("campaigns/<int:pk>/", web_view.CampaignDetailView.as_view(), name="campaign-detail"),
    path("campaigns/<int:campaign_id>/ads/create/", web_view.AdvertisementCreateView.as_view(), name="ad-create"),
    path("ads/<int:pk>/", web_view.AdvertisementDetailView.as_view(), name="ad-detail"),
    path("ads/<int:pk>/edit/", web_view.AdvertisementUpdateView.as_view(), name="ad-edit"),
    path("ads/<int:pk>/delete/", web_view.AdvertisementDeleteView.as_view(), name="ad-delete"),
    path("ads/<int:ad_id>/banners/create/", web_view.BannerCreateView.as_view(), name="banner-create"),
    path("banners/<int:pk>/edit/", web_view.BannerUpdateView.as_view(), name="banner-edit"),
    path("banners/<int:pk>/archive/", web_view.BannerArchiveView.as_view(), name="banner-archive"),
]
