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
import pandas as pd



faker = Faker()

from data_api.models import Interest

Interest.objects.all().delete()

fake_podcasts = []

df = pd.read_csv('ListOfinterests.csv')

print(df.head())

for raw in df:
    print(raw)
    _, created = Interest.objects.get_or_create(
        name=raw)

if __name__ == '__main__':
    print('Populating Complete')



