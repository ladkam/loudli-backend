from django.urls import include, path
from data_api import views
from rest_framework_simplejwt import views as jwt_views

from rest_framework.authtoken import views as authview

"""marketplace_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path('', admin.site.urls),
    url(r'^api-token-auth/', views.MyTokenObtainPairView.as_view()),
    path('podcasts/<int:pk>/', views.PodcastsDetail.as_view()),
    path('usersInfo/', views.UserProfileInfoList.as_view()),
    path('usersInfo/<int:pk>/', views.UserProfileInfoDetail.as_view()),
    path('podcasts/', views.PodcastsList.as_view()),
    path('podcastsFilter/', views.PodcastsListFilter.as_view()),
    path('episodestats/', views.PodcastatList.as_view()),
    path('episodes/', views.EpisodeList.as_view()),
    path('podcaststatGeneral/', views.PodcastStatsGeneral.as_view()),
    path('Compaign/', views.CompaignList.as_view()),
    path('Compaign/<int:pk>/', views.CompaignDetail.as_view()),
    path('Message/<int:pk>/', views.MessageDetail.as_view()),
    path('PodcastPlays/',views.PodcastPlays.as_view()),
    path('PodcastPlays/',views.PodcastPlays.as_view()),
    path('AgeGroup/', views.AgeGroupList.as_view()),
    path('Education/', views.EducationList.as_view()),
    path('Tag/', views.TagList.as_view()),
    path('Interest/', views.InterestList.as_view()),
    path('City/', views.CityList.as_view()),
    path('Country/', views.CountryList.as_view()),
    path('UpdatePodcastEpisodes/', views.UpdatePodcastEpisodes.as_view()),
    path('Messages/',views.MessagesList.as_view()),
    path('Messages-details/',views.MessageDetail.as_view()),
    path('CompaignFiles/', views.attachedList.as_view()),
    path('CompaignProposition/', views.propositionList.as_view()),
    path('auth/', include('djoser.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/customToken/', views.MyTokenObtainPairView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('validate/',views.NextCompaignStep.as_view()),
    path('decline/', views.Decline.as_view()),
    path('checkRss/',views.CheckRssPodcast.as_view()),
    path('read/',views.read.as_view()),
    path('episodesRss/',views.EpisodesPodcast.as_view()),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

