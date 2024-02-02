from django.db import models
from django.contrib.auth.models import User


class Image(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("success", "Success"),
        ("fail", "Fail"),
    ]

    image = models.ImageField(upload_to="images/")
    annotation = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")


class Comment(models.Model):
    image = models.ForeignKey(Image, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    @property
    def comment_length(self):
        return len(self.text.split())
