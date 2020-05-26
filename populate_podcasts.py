import os
# Configure settings for project
# Need to run this before calling models from application!
os.environ.setdefault('DJANGO_SETTINGS_MODULE','marketplace_api.settings')
import faker
from faker import Faker
import random

import django
import csv
# Import settings
django.setup()



faker = Faker()

from data_api.models import Podcast,Author

Podcast.objects.all().delete()
Author.object.all().delete()


exit()


sujets = ['sport','education','actualités','evenement','Science','art & culture','jeux videos','BD','politique','affaires']


fake_podcasts = []

for n in range(10):
    podcast = {}
    podcast['name'] = faker.name()
    podcast['type'] = random.choice(sujets)
    podcast['editor'] = faker.company()
    fake_podcasts.append(podcast)
    podcast['public'] = faker.domain_name()
    podcast['duration'] = random.random()*100



for podcast in fake_podcasts:

    print('in here')
    _, created = Podcast.objects.get_or_create(
        name=podcast['name'],
        type=podcast['type'],
        editor=podcast['editor'],
        public=podcast['public'],
        duration=podcast['duration']

                )


if __name__ == '__main__':
    print("Populating the databases...Please Wait")
    print('Populating Complete')
