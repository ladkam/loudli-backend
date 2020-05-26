from django.urls import include, path
from data_api import views

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
    path('podcasts/', views.PodcastsList.as_view()),
    path('podcasts/<int:pk>/', views.PodcastsDetail.as_view()),
    path('usersInfo/', views.UserProfileInfoList.as_view()),
    path('usersInfo/<int:pk>/', views.UserProfileInfoDetail.as_view()),
    path('podcasts/', views.PodcastsList.as_view()),
    path('podcastsFilter/', views.PodcastsListFilter.as_view()),
    path('episodestats/', views.PodcastatList.as_view()),
    path('episodes/', views.EpisodeList.as_view()),
    path('podcaststatGeneral/', views.PodcastStatsGeneral.as_view()),
    path('ads/', views.AdList.as_view()),
    path('ads/<int:pk>/', views.AdDetail.as_view()),
    path('Compaign/', views.CompaignList.as_view()),
    path('Compaign/<int:pk>/', views.CompaignDetail.as_view()),
    path('PodcastPlays/',views.PodcastPlays.as_view()),
    path('UpdatePodcastEpisodes/', views.UpdatePodcastEpisodes.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

