from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.postgres.fields import ArrayField
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users
from datetime import datetime
import uuid
from django.contrib.auth.models import AbstractUser


from django.contrib.auth.models import AbstractUser
import logging




def scramble_uploaded_filename(instance, filename):
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)

def scramble_uploaded_audiofilename(instance, filename):
    return 'campaign_'+str(instance.id)+'_'+filename

class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,related_name='profile',on_delete=models.CASCADE)
    first_name =models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
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




class AgeGroup(models.Model):
    ageIntervalMin = models.IntegerField()
    ageIntervalMax = models.IntegerField()
    name = models.CharField(max_length=50)

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False



class Education(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

class Location(models.Model):
    name = models.CharField(max_length=20)
def __str__(self):
    return self.name

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

class Gender(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name
    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

class Interest(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

class Country(models.Model):
    name = models.CharField(max_length=52)
    def __str__(self):
        return self.name
    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

class City(models.Model):
    name = models.CharField(max_length=52)

    def __str__(self):
        return self.name

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @authenticated_users
    def has_read_permission(self):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

class Tag(models.Model):
    name = models.CharField(max_length=52)
    def __str__(self):
        return self.name

class Podcast(models.Model):

    name = models.CharField(max_length=256)
    tags = models.ManyToManyField(Tag, blank=True)
    urlFeed = models.CharField(max_length=256, blank=True, null=True)
    image = models.CharField(max_length=256, blank=True, null=True)
    nbEpisodes = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    nbPlays = models.IntegerField()
    price = models.IntegerField()
    targetGender = models.ForeignKey(Gender,blank=True, null=True , on_delete = models.CASCADE)
    ageGroup = models.ManyToManyField(AgeGroup,blank=True,null=True)
    city = models.ManyToManyField(City,blank=True,null=True)
    country = models.ManyToManyField(Country, blank=True,null=True)
    categories = ArrayField(models.CharField(max_length=40,blank=True, null=True), blank=True, null=True)
    editor = models.CharField(max_length=128, blank=True, null=True)
    author = models.ForeignKey(User, on_delete = models.CASCADE)

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(self):
        return True
    def has_object_write_permission(self,request):
        if UserProfileInfo.objects.filter(user=request.user):
            return True
        return False

    @authenticated_users
    def has_read_permission(self):
        return True

    @authenticated_users
    def has_object_read_permission(self,request):
        return True

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_create_permission(request):
        if UserProfileInfo.objects.filter(user=request.user,type='announcer') :
            return True
        return False

    """episodesLoadingStatus = models.CharField(max_length=20,blank=True,null=True,default=('Not initialized'))
    listenNotesId = models.CharField(max_length=256,blank=True,null=True)
    genre = models.CharField(max_length=256,default='Other')
    editor = models.CharField(max_length=256,null=True)
    thumbnail = models.URLField(blank=True,null=True)
    podcastPicture = models.ImageField(blank=True,null=True,upload_to=scramble_uploaded_filename)
    duration = models.IntegerField(blank=True,null=True)
    pub_date = models.DateTimeField(blank=True,null=True)

    public = models.CharField(max_length=256)
    nb_episodes = models.IntegerField(blank=True,default=0,null=True )"""

    def __str__(self):
        return self.name

    """def image_img(self):
        if self.podcastPicture:
            return u'<img src="%s" width="50" height="50" />' % self.podcastPicture.url
        else:
            return '(Sin imagen)'"""

class episodePodcast(models.Model):
    name = models.CharField(max_length=256)
    pubDate = models.DateField(auto_now=True)
    audio = models.CharField(max_length=256,null=True,blank=True)
    image = models.CharField(max_length=256,null=True,blank=True)
    text = models.TextField(max_length=400,null=True,blank=True)
    podcast = models.ForeignKey(Podcast,on_delete=models.CASCADE)
    duration = models.IntegerField(null=True,blank=True)
    def __str__(self):
        return self.name

class Compaign(models.Model):
    name = models.CharField(max_length=256)
    startDate = models.DateField(auto_now=True)
    type = models.TextField(blank=True,null=True)
    announcer = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast,null=True,on_delete=models.CASCADE)
    description = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=20,default='Créée')
    statusNum = models.IntegerField(default=1)
    plays = models.IntegerField(blank=True,null=True)
    price = models.IntegerField(blank=True,null=True)
    targetGender = models.ForeignKey(Gender,blank=True,null=True,on_delete=models.CASCADE)
    compaignPicture = models.ImageField(blank=True,null=True,upload_to=scramble_uploaded_filename)
    actionFor = models.IntegerField(default=0,choices = [(0,0),(1,1)])
    adText =  models.TextField(max_length=2000,blank=True,null=True)
    audioFile = models.FileField(blank=True,null=True,upload_to=scramble_uploaded_audiofilename)
    audioFileName = models.CharField(max_length=128,blank=True, null=True)
    ageGroup = models.ManyToManyField(AgeGroup,blank=True)

    city = models.ManyToManyField(City,blank=True,null=True)
    country = models.ManyToManyField(Country, blank=True,null=True)
    pitch= models.TextField(max_length=2000,blank=True,null=True)
    urlProduit = models.CharField(max_length=40,blank=True, null=True)
    """
    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        if len(UserProfileInfo.objects.filter(user=request.user,type='announcer'))>0:
            return True
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        if len(UserProfileInfo.objects.filter(user=request.user,type='announcer'))>0:
            print('has')
            return True
        else:
            print('has')
            return False

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_object_write_permission(self,request):
        return True
        


    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        return True

    @staticmethod
    @authenticated_users
    def has_object_read_permission(self,request):
            return True
        return False
        """

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        if request.user == self.announcer or Podcast.objects.filter(pk=self.podcast.id,author=request.user):
            return True

    @staticmethod
    def has_write_permission(request):
            return True


    @staticmethod
    def has_create_permission(request):
        if len(UserProfileInfo.objects.filter(user=request.user, type='announcer')) > 0:
            return True
        else:
            False

    def has_object_write_permission(self,request):
        if request.user == self.announcer or Podcast.objects.filter(pk=self.podcast.id,author=request.user):
            return True

    def __str__(self):
        return self.name




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


class attached(models.Model):
    attachedFile = models.FileField(blank=True,null=True,upload_to=scramble_uploaded_filename)
    attachedFileName = models.TextField(blank=True, null=True)
    compaign = models.ForeignKey(Compaign, on_delete=models.CASCADE)


class Message(models.Model):
    sendDate = models.DateTimeField(auto_now=True)
    text =  models.TextField(blank=True,null=True)
    readFlag = models.BooleanField(default=False)
    compaign = models.ForeignKey(Compaign, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    attachedFile = models.FileField(blank=True,null=True,upload_to=scramble_uploaded_filename)
    attachedFileName = models.TextField(blank=True, null=True)

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_write_permission(request):
        return True

    @staticmethod
    @authenticated_users
    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_create_permission(request):
        return False