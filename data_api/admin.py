from django.contrib import admin
from .models import Podcast,UserProfileInfo,Ad,Compaign,EpisodeStat,PodcastStatGeneral,Episode,EpisodeImported

# Register your models here.

admin.site.register(Podcast)
admin.site.register(UserProfileInfo)
admin.site.register(Ad)
#admin.site.register(Author)
#admin.site.register(Announcer)
admin.site.register(Compaign)
admin.site.register(EpisodeStat)
admin.site.register(PodcastStatGeneral)
admin.site.register(Episode)
admin.site.register(EpisodeImported)
