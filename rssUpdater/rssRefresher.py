from data_api.models import Podcast,episodePodcast
from pyPodcastParser.Podcast import Podcast as PodcastParser
import requests

def update_rss():
    podcastList = Podcast.objects.all()
    for pod in podcastList:
        url = pod.urlFeed
        response=requests.get(url)
        items = PodcastParser(response.content).items
        for item in items:
            title = item.title
            link = item.enclosure_url
            image = item.itune_image
            text = item.description
        _,created = episodePodcast.objects.update_or_create(name = title,text=text,audio=link,image=image,podcast=pod)








