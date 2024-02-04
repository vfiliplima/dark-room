import pytest
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Image, Comment

import os


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

    detail_url = f"/images/{test_image.id}/"
    response = api_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK

    assert response.data["annotation"] == test_image.annotation
    assert response.data["status"] == test_image.status

    list_response = api_client.get("/images/")
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data) == 1


@pytest.mark.django_db
def test_image_create_view(api_client, test_user):

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


@pytest.mark.django_db
def test_image_update_view(api_client, test_user, test_image):
    api_client.force_authenticate(test_user)
    image_detail_url = f"/images/{test_image.id}/"

    response = api_client.patch(image_detail_url, data={"status": "processing"})

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_image_update_view_unauthenticated(api_client, test_image):
    image_detail_url = f"/images/{test_image.id}/"

    response = api_client.patch(image_detail_url, data={"status": "fail"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Authentication credentials were not provided" in str(response.content)


@pytest.mark.django_db
def test_comment_create_view(api_client, test_user, test_image):
    api_client.force_authenticate(test_user)
    comment_post_url = f"/images/{test_image.id}/comments/"

    comment_list_initial = Comment.objects.filter(image_id=test_image.id)
    assert len(comment_list_initial) == 0

    response = api_client.post(comment_post_url, data={"text": "Nice stuff"})
    assert response.status_code == status.HTTP_201_CREATED

    comment_list_post = Comment.objects.filter(image_id=test_image.id)
    assert len(comment_list_post) == 1
    assert comment_list_post[0].text == "Nice stuff"


@pytest.mark.django_db
def test_comment_create_view_not_found(api_client, test_user):
    api_client.force_authenticate(test_user)
    comment_post_url = f"/images/{99}/comments/"

    response = api_client.post(comment_post_url, data={"text": "hein?"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comment_delete_view(api_client, test_user, test_image):
    api_client.force_authenticate(test_user)
    new_comment = Comment.objects.create(
        image=test_image, user=test_user, text="temp comment"
    )
    comment_delete_url = f"/images/{test_image.id}/comments/{new_comment.id}/delete/"

    response = api_client.delete(comment_delete_url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(id=new_comment.id).exists()
