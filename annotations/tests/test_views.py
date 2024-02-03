import pytest
from django.contrib.auth.models import User
from django.conf import settings
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
        image="http://127.0.0.1:8000/images/GOPR1853.JPG",
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


@pytest.mark.django_db
def test_image_detail_view(api_client, test_user, test_image):
    api_client.force_authenticate(user=test_user)
    i1 = test_image
    i1_id = i1.id
    detail_url = f"/images/{i1_id}/"
    response = api_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == i1_id

    list_response = api_client.get("/images/")
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data) == 1


@pytest.mark.django_db
def test_image_create_view(api_client, test_user):
    import os

    api_client.force_authenticate(user=test_user)

    file_name = "GOPR1813.JPG"
    file_path = os.path.join(settings.MEDIA_ROOT, "images", file_name)

    response = api_client.post(
        "/images/",
        data={
            "image": open(file_path, "rb"),
            "user": 1,
            "status": "queued",
            "annotation": "mountain",
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
