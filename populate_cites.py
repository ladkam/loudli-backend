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

from data_api.models import City
from data_api.models import Country

City.objects.all().delete()
Country.objects.all().delete()

df = pd.read_csv('worldcities.csv')

for country in df['country'].unique()[1]:
    CountryObj, created = Country.objects.get_or_create(name=country)
    for city in df[df['country']==country].city:
        CountryObj, created = City.objects.get_or_create(name=city,country=CountryObj)









