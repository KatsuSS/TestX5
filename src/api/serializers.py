from rest_framework import serializers

from core.models import ads as ads_models


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads_models.Campaign
        fields = [
            "id",
            "name",
            "user",
            "start_date",
            "end_date",
            "budget",
            "strategy",
            "max_impressions_per_day",
            "targeting",
        ]
        read_only_fields = ["id", "user"]

    def validate(self, data):
        start = data["start_date"]
        end = data["end_date"]
        if end < start:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала")

        strategy = data["strategy"]
        max_impressions = data.get("max_impressions_per_day")
        if strategy == ads_models.Campaign.SpendingStrategy.MAX_IMPRESSIONS.value and max_impressions is None:
            raise serializers.ValidationError("Нужно указать для стратегии 'максимальные показы'")
        if strategy == ads_models.Campaign.SpendingStrategy.EVENLY.value and max_impressions is not None:
            raise serializers.ValidationError("Используется только для стратегии 'максимальные показы'")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads_models.Advertisement
        fields = [
            "id",
            "name",
            "campaign",
            "place",
            "url",
            "description",
        ]
        read_only_fields = ["id", "campaign"]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads_models.Banner
        fields = [
            "id",
            "advertisement",
            "uid",
            "width",
            "height",
            "file",
            "is_active",
        ]
        read_only_fields = ["id", "advertisement"]
