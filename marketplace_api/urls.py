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
    path('api/', admin.site.urls),
    path('api/podcasts/', views.PodcastsList.as_view()),
    path('api/podcasts/<int:pk>/', views.PodcastsDetail.as_view()),
    path('api/usersInfo/', views.UserProfileInfoList.as_view()),
    path('api/usersInfo/<int:pk>/', views.UserProfileInfoDetail.as_view()),
    path('api/podcasts/', views.PodcastsList.as_view()),
    path('api/podcastsFilter/', views.PodcastsListFilter.as_view()),
    path('api/episodestats/', views.PodcastatList.as_view()),
    path('api/episodes/', views.EpisodeList.as_view()),
    path('api/podcaststatGeneral/', views.PodcastStatsGeneral.as_view()),
    path('api/ads/', views.AdList.as_view()),
    path('api/ads/<int:pk>/', views.AdDetail.as_view()),
    path('api/Compaign/', views.CompaignList.as_view()),
    path('api/Compaign/<int:pk>/', views.CompaignDetail.as_view()),
    path('api/PodcastPlays/',views.PodcastPlays.as_view()),
    path('api/UpdatePodcastEpisodes/', views.UpdatePodcastEpisodes.as_view()),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

