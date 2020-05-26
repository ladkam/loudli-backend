from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime
import uuid

def scramble_uploaded_filename(instance, filename):
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)

class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    company = models.CharField(max_length=256)
    Type = models.CharField(max_length=256)
    """
    profilePicture = models.ImageField(blank=True,upload_to=scramble_uploaded_filename)

    def image_img(self):
        if self.profilePicture:
            return u'<img src="%s" width="50" height="50" />' % self.profilePicture.url
        else:
            return '(Sin imagen)'
    profilePicture.short_description = 'Thumb'
    profilePicture.allow_tags = True

    @receiver(post_save, sender=user)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfileInfo.objects.create(user=instance)
# Create your models here.
"""

class Compaign(models.Model):
    name = models.CharField(max_length=256)
    startDate = models.DateField(auto_now=True)
    announcer = models.ForeignKey(User, on_delete=models.CASCADE)
    compaignPicture = models.ImageField(blank=True,upload_to=scramble_uploaded_filename)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    name = models.CharField(max_length=256 )
    listenNotesId = models.CharField(max_length=256,blank=True,null=True)
    genre = models.CharField(max_length=256,null=True)
    editor = models.CharField(max_length=256,null=True)
    thumbnail = models.URLField(blank=True,null=True)
    podcastPicture = models.ImageField(blank=True,null=True,upload_to=scramble_uploaded_filename)
    duration = models.IntegerField(blank=True,null=True)
    pub_date = models.DateTimeField(blank=True,null=True)
    about = models.TextField()
    public = models.CharField(max_length=256)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    nb_episodes = models.IntegerField(blank=True,default=0,null=True )
    def __str__(self):
        return self.name
    def image_img(self):
        if self.podcastPicture:
            return u'<img src="%s" width="50" height="50" />' % self.podcastPicture.url
        else:
            return '(Sin imagen)'

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    def __str__(self):
        return self.name
    listenNotesId = models.CharField(max_length=256,blank=True)
    link = models.URLField(blank=True,null=True )
    audio = models.URLField(blank=True,null=True )
    image = models.URLField(blank=True,null=True )
    title = models.CharField(max_length=256,blank=True,null=True )
    thumbnail = models.CharField(max_length=256,blank=True,null=True )
    description = models.TextField(blank=True,null=True)
    pub_date_ms = models.DateTimeField(blank=True,default=None,null=True)
    pub_date = models.DateField(blank=True,null=True)
    audio_length_sec = models.IntegerField(blank=True,default=0,null=True )
    explicit_content = models.BooleanField(blank=True,default=False,null=True )

class EpisodeImported(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

class EpisodeStat(models.Model):
    episode = models.ForeignKey(EpisodeImported, on_delete=models.CASCADE)
    date = models.DateField()
    updateDate = models.DateField(auto_now_add=True, blank=True)
    plays = models.IntegerField()

class PodcastStatGeneral(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    plays = models.IntegerField()
    nbEpisodes = models.IntegerField()

class Ad(models.Model):
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=256)
    startDate = models.DateField(auto_now=True)
    status = models.CharField(max_length=256)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    compaign = models.ForeignKey(Compaign, on_delete=models.CASCADE)
    Requesttext = models.TextField()
    def __str__(self):
        return self.name

