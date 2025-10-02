from django.db import models

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    credits = models.FloatField()