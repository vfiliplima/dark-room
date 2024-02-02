from rest_framework import generics, serializers
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from textblob import TextBlob

from .models import Image, Comment
from .serializers import ImageSerializer, CommentSerializer
from .annotations_gen import mock_annotation_processing


class ImageListCreateView(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def perform_create(self, serializer):
        if "image" not in self.request.data:
            raise serializers.ValidationError({"image": "This field is required."})
        instance = serializer.save()
        instance.status = "processing"
        instance.save()

        annotation = mock_annotation_processing()
        print(f"Annotation: {annotation}")
        instance.annotation = annotation

        if annotation:
            instance.status = "success"
        else:
            instance.status = "fail"
        instance.save()


class ImageDetailView(generics.RetrieveUpdateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        image_id = self.kwargs.get("image_id")
        image = generics.get_object_or_404(Image, pk=image_id)
        serializer.save(image=image, user=self.request.user)


class UserImagesListView(generics.ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter images based on the authenticated user
        return Image.objects.filter(user=self.request.user)


class ImageDeleteView(generics.DestroyAPIView):
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
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAdminUser]  # Only admin users can delete images

    def get_object(self):
        image_id = self.kwargs.get("image_id")
        image = generics.get_object_or_404(Image, pk=image_id)
        return image
