from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from core.models import ads as ad_models
from web import forms


class CampaignListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):  # TODO: LOGIC-7
    model = ad_models.Campaign
    template_name = "campaigns/campaign_list.html"
    context_object_name = "campaigns"
    paginate_by = 2
    permission_required = "core.view_campaign"

    def get_queryset(self):
        queryset = ad_models.Campaign.objects.filter(user=self.request.user).annotate(
            banner_count=Count("advertisements__banners", distinct=True)
        )

        for campaign in queryset:  # TODO: DJANGO-1
            formats = ad_models.Banner.objects.filter(advertisement__campaign=campaign).values_list("file", flat=True)
            unique_formats = {f.split(".")[-1].lower() for f in formats}
            campaign.file_formats = ", ".join(unique_formats) if unique_formats else ""  # ", ".join(set()) уже даст пустую строку, нет сортировки

        return queryset


class CampaignCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ad_models.Campaign
    form_class = forms.CampaignForm
    template_name = "campaigns/campaign_form.html"
    success_url = reverse_lazy("web:campaign-list")
    permission_required = "core.add_campaign"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CampaignDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ad_models.Campaign
    template_name = "campaigns/campaign_detail.html"
    context_object_name = "campaign"
    permission_required = "core.view_advertisement"  # TODO: LOGIC-1

    def get_queryset(self):
        return ad_models.Campaign.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ads = ad_models.Advertisement.objects.filter(campaign=self.object).annotate(
            banner_count=Count("banners", distinct=True)
        )

        for ad in ads:  # TODO: DJANGO-2
            files = ad_models.Banner.objects.filter(advertisement=ad).values_list("file", flat=True)
            formats = {f.split(".")[-1].lower() for f in files}
            ad.file_formats = ", ".join(formats) if formats else ""

        context["ads"] = ads
        return context


class CampaignMixin:
    model = ad_models.Campaign
    success_url = reverse_lazy("web:campaign-list")

    def get_queryset(self):
        return ad_models.Campaign.objects.filter(user=self.request.user)


class CampaignUpdateView(CampaignMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = forms.CampaignForm
    template_name = "campaigns/campaign_form.html"
    permission_required = "core.change_campaign"


class CampaignDeleteView(CampaignMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = "campaigns/campaign_delete.html"
    permission_required = "core.delete_campaign"


class AdvertisementCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ad_models.Advertisement
    form_class = forms.AdvertisementForm
    template_name = "advertisement/advertisement_form.html"
    permission_required = "core.add_advertisement"

    def dispatch(self, request, *args, **kwargs):
        self.campaign = ad_models.Campaign.objects.get(pk=kwargs["campaign_id"], user=request.user)  # TODO: SEC-5
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("web:campaign-detail", args=[self.campaign.id])


class AdvertisementDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ad_models.Advertisement
    template_name = "advertisement/advertisement_detail.html"
    context_object_name = "ad"
    permission_required = "core.view_banner"  # TODO: LOGIC-2

    def get_queryset(self):
        return ad_models.Advertisement.objects.filter(campaign__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        banners = ad_models.Banner.objects.filter(advertisement=self.object)
        for banner in banners:  # TODO: DJANGO-3
            banner.file_format = banner.file.name.split(".")[-1].lower()

        context["banners"] = banners
        return context


class AdvertisementMixin:
    model = ad_models.Advertisement

    def get_queryset(self):
        return ad_models.Advertisement.objects.filter(campaign__user=self.request.user)

    def get_success_url(self):
        return reverse("web:campaign-detail", args=[self.object.campaign.id])


class AdvertisementUpdateView(AdvertisementMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = forms.AdvertisementForm
    template_name = "advertisement/advertisement_form.html"
    permission_required = "core.change_advertisement"


class AdvertisementDeleteView(AdvertisementMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = "advertisement/advertisement_delete.html"
    permission_required = "core.delete_advertisement"


class BannerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ad_models.Banner
    form_class = forms.BannerForm
    template_name = "banner/banner_form.html"
    permission_required = "core.add_banner"

    def dispatch(self, request, *args, **kwargs):
        self.ad = ad_models.Advertisement.objects.get(pk=kwargs["ad_id"], campaign__user=request.user)  # TODO: SEC-5
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ad"] = self.ad
        return context

    def form_valid(self, form):
        form.instance.advertisement = self.ad
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("web:ad-detail", args=[self.ad.id])


class BannerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ad_models.Banner
    form_class = forms.BannerForm
    template_name = "banner/banner_form.html"
    permission_required = "core.change_banner"

    def get_queryset(self):
        return ad_models.Banner.objects.filter(advertisement__campaign__user=self.request.user)

    def get_success_url(self):
        return reverse("web:ad-detail", args=[self.object.advertisement.id])


class BannerArchiveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "core.change_banner"

    def post(self, request, pk):
        banner = ad_models.Banner.objects.get(pk=pk, advertisement__campaign__user=request.user)  # TODO: SEC-5
        banner.is_active = False
        banner.save(update_fields=["is_active"])  # TODO: ERR-3
        return redirect("web:ad-detail", banner.advertisement.id)
