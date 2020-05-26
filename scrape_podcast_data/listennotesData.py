import requests
import json
import sys
import django
import os
import time
import io
import sys
import time
from pathlib import Path
import django
from django.conf import settings
from django.db import models
from datetime import datetime
# add project root to sys path
sys.path.append(sys.path.append('/Users/amine/work/django_api_marketPlace/marketplace_api'))
# set up the Django enviroment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "marketplace_api.settings")
django.setup()
# import the History class from web app's models.py
from data_api.models import Podcast,Episode
from django.utils.timezone import make_aware
# here we can add useful snippet of code for doing our stuff

class podcast:
    def __init__(self,podcastId):
        podcast.listenNotesId = Podcast.objects.get(id=podcastId).listenNotesId
        print('here')
        print(podcast.listenNotesId)
        podcast.url = 'https://listen-api.listennotes.com/api/v2/podcasts/'+self.listenNotesId
        podcast.headers = {'X-ListenAPI-Key': '4e1755f6cd57457596b9d3bb5aec44fc'}
        podcast.instance = Podcast.objects.get(id=podcastId)
        podcast.podcastId = podcastId

    def get_Episodes(self):
        response = requests.get(
            self.url,
            headers = self.headers
        )
        return [response.json()['episodes'],response.json()['total_episodes']]

    def drop_episodes(self):
        Episode.objects.filter(podcast=self.podcastId).delete()

    def add_episodes(self,episodes):
        print(episodes[1])
        pod=Podcast.objects.get(id=self.podcastId)
        setattr(pod, 'nb_episodes', episodes[1])
        pod.save()

        for episode in episodes[0]:
            Episode.objects.create(
            podcast=self.instance,
            name = episode['title'],
            pub_date = make_aware(datetime.fromtimestamp(episode['pub_date_ms']/1000)),
            listenNotesId = episode['id'],
            link = episode['link'],
            audio = episode['audio'],
            image = episode['image'],
            title = episode['title'],
            thumbnail = episode['thumbnail'],
            description = episode['description'],
            audio_length_sec = episode['audio_length_sec'],
            explicit_content = episode['explicit_content'])


    def update_episodes(self):
        self.drop_episodes()
        Episodes = self.get_Episodes()
        self.add_episodes(Episodes)
        print('Data Imported')