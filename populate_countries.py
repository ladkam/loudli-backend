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

Country.objects.all().delete()

df = pd.read_csv('countries.csv')

for index,row in df.iterrows():
    _, created = Country.objects.get_or_create(name=row['Country FR'])










