from django.db import models
from django.contrib.auth.models import User
# from django.utils import timezone

# Create your models here.

class BlogPost(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    yt_video_title = models.CharField(max_length=300)
    yt_video_link = models.URLField()
    yt_video_transcript = models.TextField()  # WHEN WE GET generator_content, AFTER THAT WE DONT USE TRANSCRIPT 
    created_at = models.DateTimeField(auto_now_add=True)
    # created_at = models.DateTimeField(default=timezone.now)



    def __str__(self):
        return self.yt_video_title