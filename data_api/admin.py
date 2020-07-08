from django.contrib import admin
from .models import Podcast,episodePodcast,UserProfileInfo,Tag,CompaignAttachedFile,Compaign,EpisodeStat,PodcastStatGeneral,Episode,EpisodeImported,Message,AgeGroup,Interest,City,Country
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

admin.site.register(Podcast)
admin.site.register(UserProfileInfo)
#admin.site.register(Author)
#admin.site.register(Announcer)
admin.site.register(Compaign)
admin.site.register(EpisodeStat)
admin.site.register(PodcastStatGeneral)
admin.site.register(Episode)
admin.site.register(EpisodeImported)
admin.site.register(Message)
admin.site.register(AgeGroup)
admin.site.register(Interest)
admin.site.register(City)
admin.site.register(Country)
admin.site.register(CompaignAttachedFile)
admin.site.register(Tag)
admin.site.register(episodePodcast)







