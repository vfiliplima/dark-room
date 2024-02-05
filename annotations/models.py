from django.db import models
from django.contrib.auth.models import User
import random
import time
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver


class Annotation(models.Model):
    EXISTING_ANNOTATIONS = [
        ("boat", "Boat"),
        ("mountain", "Mountain"),
        ("plains", "Plains"),
        ("ocean", "Ocean"),
        ("forest", "Forest"),
    ]
    annotation = models.CharField(
        max_length=40, choices=EXISTING_ANNOTATIONS, default=None
    )


class Image(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("success", "Success"),
        ("fail", "Fail"),
    ]

    image = models.ImageField(upload_to="media/images/")
    annotation = models.ManyToManyField(Annotation, related_name="images", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")

    def process_annotations(self):
        if self.annotation.count() == 1:
            self.status = "processing"
            self.save()
        elif self.annotation.count() == len(Annotation.EXISTING_ANNOTATIONS):
            self.status = "success"
            self.save()

    def add_random_annotation(self):
        # random wait time(sleep)
        sleep_time = random.randint(5, 50)
        time.sleep(sleep_time)

        # pick a random annotation
        random_annotation = random.choice(Annotation.EXISTING_ANNOTATIONS)

        # Add the annotation to the image
        annotation_obj, _ = Annotation.objects.get_or_create(
            annotation=random_annotation[0]
        )
        self.annotation.add(annotation_obj)


@receiver(post_save, sender=Image)
def annotate_image(instance, **kwargs):

    instance.add_random_annotation()


@receiver(m2m_changed, sender=Image.annotation.through)
def process_annotations(sender, instance, action, **kwargs):
    if action == "post_add":
        instance.process_annotations()


class Comment(models.Model):
    image = models.ForeignKey(Image, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    @property
    def comment_length(self):
        return len(self.text.split())
