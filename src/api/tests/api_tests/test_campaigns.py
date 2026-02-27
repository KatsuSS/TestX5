import datetime

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_campaign_list_without_auth(simple_api_client, campaign):
    url = reverse("api:campaigns")
    response = simple_api_client.get(url, content_type="application/json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_campaign_list_for_superuser(auth_super_client, campaign_super_user):
    url = reverse("api:campaigns")
    response = auth_super_client.get(url, content_type="application/json")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Test campaign super user"


@pytest.mark.django_db
def test_campaign_list_for_superuser_with_user_campaign(auth_super_client, campaign_super_user, campaign):
    url = reverse("api:campaigns")
    response = auth_super_client.get(url, content_type="application/json")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Test campaign super user"


@pytest.mark.django_db
def test_campaign_list_for_user(auth_client, user_view_group, campaign):
    url = reverse("api:campaigns")
    response = auth_client.get(url, content_type="application/json")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Test campaign user"


@pytest.mark.django_db
def test_create_campaign_for_superuser(auth_super_client):
    url = reverse("api:campaigns")
    data = {
        "name": "New campaign supseruser",
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today(),
        "budget": 1000,
        "strategy": "evenly",
    }
    response = auth_super_client.post(url, data)

    assert response.status_code == 201
    assert response.data["name"] == "New campaign supseruser"


@pytest.mark.django_db
def test_create_campaign_without_auth(simple_api_client):
    url = reverse("api:campaigns")
    data = {
        "name": "New campaign supseruser",
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today(),
        "budget": 1000,
        "strategy": "evenly",
    }
    response = simple_api_client.post(url, data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_campaign_without_perms(auth_client):
    url = reverse("api:campaigns")
    data = {
        "name": "New campaign supseruser",
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today(),
        "budget": 1000,
        "strategy": "evenly",
    }
    response = auth_client.post(url, data)

    assert response.status_code == 403


@pytest.mark.parametrize(
    "data",
    [
        {"name": "only_name"},
        {
            "name": "name",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() - datetime.timedelta(days=1),
            "budget": 1000,
            "strategy": "evenly",
        },
        {
            "name": "name",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "budget": -1000,
            "strategy": "evenly",
        },
        {
            "name": "name",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "budget": 100,
            "strategy": "max_impressions",
        },
        {
            "name": "name",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "budget": 100,
            "strategy": "max_impressions",
            "max_impressions_per_day": -10,
        },
        {
            "name": "name",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today(),
            "budget": 100,
            "strategy": "max_impressions",
            "max_impressions_per_day": 2_000_000,
        },
    ],
)
@pytest.mark.django_db
def test_create_campaign_with_invalid_values(auth_super_client, data):
    url = reverse("api:campaigns")
    response = auth_super_client.post(url, data)
    assert response.status_code == 400
