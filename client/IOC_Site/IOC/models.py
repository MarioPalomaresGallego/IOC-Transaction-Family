from django.db import models

# Create your models here.

class Upload(models.Model):
    sample_name = models.CharField(max_length=200)
    report_name = models.CharField(max_length=200)
    date = models.DateTimeField()
    batch_id = models.CharField(max_length=130)
    status = models.CharField(max_length=10)
