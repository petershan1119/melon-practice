from django.db import models

class Youtube(models.Model):
    video_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.title} | {self.video_id}'
