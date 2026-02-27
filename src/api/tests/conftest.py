import datetime

import pytest
from django.contrib.auth.models import Group, Permission
from rest_framework.test import APIClient

from core.models import ads as ad_models
from core.models import users as user_models


@pytest.fixture
def simple_api_client():
    client = APIClient()
    return client


@pytest.fixture
def super_user():
    return user_models.User.objects.create_user(username="testsuperuser", password="12345", is_superuser=True)


@pytest.fixture
def user():
    return user_models.User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def user_view_group(user):
    view_group = Group.objects.create(name="View group")
    view_group.permissions.add(Permission.objects.get(codename="view_campaign"))
    view_group.permissions.add(Permission.objects.get(codename="view_advertisement"))
    view_group.permissions.add(Permission.objects.get(codename="view_banner"))
    user.groups.add(view_group)


@pytest.fixture
def auth_super_client(simple_api_client, super_user):
    simple_api_client.force_authenticate(user=super_user)
    return simple_api_client


@pytest.fixture
def auth_client(simple_api_client, user):
    simple_api_client.force_authenticate(user=user)
    return simple_api_client


@pytest.fixture
def campaign_super_user(super_user):
    return ad_models.Campaign.objects.create(
        name="Test campaign super user",
        start_date=datetime.date.today(),
        end_date=datetime.date.today(),
        budget=1000,
        strategy=ad_models.Campaign.SpendingStrategy.EVENLY,
        user=super_user,
    )


@pytest.fixture
def campaign(user):
    return ad_models.Campaign.objects.create(
        name="Test campaign user",
        start_date=datetime.date.today(),
        end_date=datetime.date.today(),
        budget=1000,
        strategy=ad_models.Campaign.SpendingStrategy.EVENLY,
        user=user,
    )
