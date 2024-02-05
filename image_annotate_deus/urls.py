"""image_annotate_deus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from annotations.views import (
    ImageListView,
    ImageCreateView,
    ImageDetailView,
    CommentCreateView,
    UserImagesListView,
    ImageDeleteView,
    CommentDeleteView,
    AdminImageDeleteView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("images/", ImageListView.as_view(), name="image-list"),
    path("images/create/", ImageCreateView.as_view(), name="image-create"),
    path("images/<int:pk>/", ImageDetailView.as_view(), name="image-detail"),
    path(
        "images/<int:image_id>/admin/",
        AdminImageDeleteView.as_view(),
        name="image-delete",
    ),
    path(
        "images/<int:image_id>/comments/",
        CommentCreateView.as_view(),
        name="comment-create",
    ),
    path(
        "images/<int:image_id>/delete/",
        ImageDeleteView.as_view(),
        name="own-image-delete",
    ),
    path(
        "images/<int:image_id>/comments/<int:comment_id>/delete/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
    path("user/images/", UserImagesListView.as_view(), name="user-images-list"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
