import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Image, Comment


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def test_image(test_user):
    return Image.objects.create(
        image="../../images/GOPR1795.JPG",
        annotation="Test Annotation",
        user=test_user,
        status="success",
    )


@pytest.fixture
def test_comment(test_image, test_user):
    return Comment.objects.create(image=test_image, user=test_user, text="Test Comment")


@pytest.mark.django_db
def test_image_list_create_view(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    response = api_client.get("/images/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
