import os

from django.db import models
from django.utils.timezone import now
from random import randint

# Create your models here.


def image_upload_path(instance, filename):
    filename_base, filename_ext = os.path.splitext(instance.image.name)
    return (
        "sharkle/"
        + now().strftime("%Y%m%d")
        + "_"
        + str(randint(10000000, 99999999))
        + filename_ext  # ex) 20220724_60991341.png
    )


class Image(models.Model):  # TODO Basemodel?
    title = models.CharField(max_length=100, blank=True)
    image = models.FileField(upload_to=image_upload_path)

    def __str__(self):
        return self.title
