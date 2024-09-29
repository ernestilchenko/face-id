from django.db import models


class Webcam(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='faces/')

    def __str__(self):
        return self.name
