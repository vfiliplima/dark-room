from rest_framework import generics, serializers
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from textblob import TextBlob

from .models import Image, Comment
from .serializers import (
    ImageSerializer,
    ImageCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)


class ImageListView(generics.ListAPIView):
    """
    Get a list of images.

    This endpoint allows users to retrieve a list of images.

    __Returns__: A list of images.


    __Status Codes:__
    - 200 OK: Successful retrieval of the image list.
    - 403 Forbidden: Authentication required for image creation.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authorization__:
    - All authenticated users have access to listing images.
    - Only authenticated users can create new images.

    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]


class ImageCreateView(generics.CreateAPIView):
    """
    Create a new image.

    This endpoint allows authenticated users to upload and create a new image.

    __Request Example__:
    ```
    POST /images/
    Headers: {'Authorization': 'Token <your_token>', 'Content-Type': 'multipart/form-data'}
    Body: {'image': [file]}
    ```

    __Returns__: A success message or error details.


    __Status Codes:__
    - 201 Created: Image successfully created.
    - 400 Bad Request: Invalid request parameters or missing image file.
    - 403 Forbidden: Authentication required.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authorization__:
    - Only authenticated users can create new images.

    """

    queryset = Image.objects.all()
    serializer_class = ImageCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if "image" not in self.request.data:
            raise serializers.ValidationError({"image": "This field is required."})
        instance = serializer.save()
        instance.save()


class ImageDetailView(generics.RetrieveAPIView):
    """
    Retrieve or update details of a specific image.

    This endpoint allows users to retrieve details or update information about a specific image.

    __Returns__: Details of the requested image, including associated comments and summary.

    Example to retrieve details of an image:
    ```
    GET /images/{image_id}/
    ```

    Example to update details of an image:
    ```
    PUT /images/{image_id}/
    Headers: {'Content-Type': 'multipart/form-data'}
    Body: {'image': [new_uri_string], 'annotation': 'Updated annotation'}
    ```

    __Note__:
    - Image updates require authentication.
    - Only the owner of the image can update its details.

    __Status Codes:__
    - 200 OK: Successful retrieval or update of the image details.
    - 400 Bad Request: Invalid query parameters or update request.
    - 403 Forbidden: Authentication required for image updates.
    - 404 Not Found: The requested image does not exist.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authentication__:
    - This endpoint requires authentication for image updates.

    __Authorization__:
    - All authenticated users can retrieve details of any image.
    - Only the owner of the image can update its details.

    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            # Retrieve all comments related to the image
            comments_queryset = Comment.objects.filter(image=instance)
            comments_serializer = CommentSerializer(comments_queryset, many=True)

            num_users_commented = (
                Comment.objects.filter(image=instance).values("user").distinct().count()
            )
            list_comment_length = [
                comment.comment_length for comment in comments_queryset
            ]

            avg_comment_length = 0
            if comments_queryset:
                avg_comment_length = sum(list_comment_length) / len(list_comment_length)

            sentiment_scores = []
            for comment in comments_queryset:
                analysis = TextBlob(comment.text)
                sentiment_scores.append(analysis.sentiment.polarity)

            # Calculate average sentiment score for all comments
            if sentiment_scores:
                average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            else:
                average_sentiment = None

            image_summary = dict(
                num_users_comment=num_users_commented,
                avg_comment_length=avg_comment_length,
                sentiment=average_sentiment,
            )
            # Add comments to the serialized data
            data = serializer.data
            data["comments"] = comments_serializer.data
            # Add summary to the serialized data
            data["summary"] = image_summary

            return Response(data)
        except Image.DoesNotExist:
            raise NotFound("Image not found")


class CommentCreateView(generics.CreateAPIView):
    """
    Create a new comment for a specific image.

    This endpoint allows users to create a new comment for a specific image.

    Example to create a new comment:
    ```
    POST /images/{image_id}/comments/
    Body: {'text': 'Great shot!'}
    ```

    __Note__:
    - Comment creation requires authentication.

    __Status Codes:__
    - 201 Created: Comment successfully created.
    - 400 Bad Request: Invalid comment creation request.
    - 403 Forbidden: Authentication required for comment creation.
    - 404 Not Found: The associated image does not exist.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authentication__:
    - This endpoint requires authentication for comment creation.

    __Authorization__:
    - All authenticated users can create comments.

    """

    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        image_id = self.kwargs.get("image_id")
        image = generics.get_object_or_404(Image, pk=image_id)
        serializer.save(image=image, user=self.request.user)


class UserImagesListView(generics.ListAPIView):
    """
    Get a list of images uploaded by the authenticated user.

    This endpoint allows users to retrieve a list of images uploaded by the authenticated user.

    __Returns__: A list of images uploaded by the authenticated user.

    Example:
    ```
    GET /user/images/
    ```

    __Note__:
    - Image retrieval requires authentication.

    __Status Codes:__
    - 200 OK: Successful retrieval of the user's image list.
    - 403 Forbidden: Authentication required for image retrieval.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authentication__:
    - This endpoint requires authentication for image retrieval.

    __Authorization__:
    - All authenticated users can retrieve their own image list.

    """

    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter images based on the authenticated user
        return Image.objects.filter(user=self.request.user)


class ImageDeleteView(generics.DestroyAPIView):
    """
    Delete an image.

    This endpoint allows the owner of an image to delete it.

    __Returns__: A success message for image deletion.

    Example:
    ```
    DELETE /images/{image_id}/
    ```

    __Note__:
    - Image deletion requires authentication and ownership.

    __Status Codes:__
    - 204 No Content: Image successfully deleted.
    - 401 Unauthorized: Authentication credentials were not provided.
    - 403 Forbidden: You do not have permission to delete this image.
    - 404 Not Found: Image not found.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authentication__:
    - This endpoint requires authentication for image deletion.

    __Authorization__:
    - The requesting user must be the owner of the image to delete it.

    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        image_id = self.kwargs.get("image_id")
        image = generics.get_object_or_404(Image, pk=image_id)

        # Check if the requesting user is the owner of the image
        if image.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this image.")

        return image


class CommentDeleteView(generics.DestroyAPIView):
    """
    Delete a comment.

    This endpoint allows the owner of a comment to delete it.

    __Returns__: A success message for comment deletion.

    Example:
    ```
    DELETE /comments/{comment_id}/
    ```

    __Note__:
    - Comment deletion requires authentication and ownership.

    __Status Codes:__
    - 204 No Content: Comment successfully deleted.
    - 401 Unauthorized: Authentication credentials were not provided.
    - 403 Forbidden: You do not have permission to delete this comment.
    - 404 Not Found: Comment not found.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authentication__:
    - This endpoint requires authentication for comment deletion.

    __Authorization__:
    - The requesting user must be the owner of the comment to delete it.

    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        comment_id = self.kwargs.get("comment_id")
        comment = generics.get_object_or_404(Comment, pk=comment_id)

        # Check if the requesting user is the owner of the comment
        if comment.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")

        return comment


class AdminImageDeleteView(generics.DestroyAPIView):
    """
    Delete an image as an admin.

    This endpoint allows an admin user to delete any image.

    __Returns__: A success message for image deletion.

    Example:
    ```
    DELETE /admin/images/{image_id}/
    ```

    __Note__:
    - Image deletion by admin requires admin authentication.

    __Status Codes:__
    - 204 No Content: Image successfully deleted.
    - 401 Unauthorized: Admin authentication credentials were not provided.
    - 404 Not Found: Image not found.
    - 500 Internal Server Error: An unexpected error occurred.

    __Authentication__:
    - This endpoint requires admin authentication for image deletion.

    __Authorization__:
    - Admin users have the authority to delete any image.

    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAdminUser]  # Only admin users can delete images

    def get_object(self):
        image_id = self.kwargs.get("image_id")
        image = generics.get_object_or_404(Image, pk=image_id)
        return image
