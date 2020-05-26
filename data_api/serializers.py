from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Podcast,UserProfileInfo,Ad,Compaign,EpisodeStat,PodcastStatGeneral,Episode

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class UserProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileInfo
        fields = '__all__'

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class PodcastsSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Podcast
        fields = '__all__'

class PodcastsSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = '__all__'

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields =  '__all__'

class EpisodeImportedSerializer(serializers.ModelSerializer):
    podcast = PodcastsSerializerPost(read_only=True)
    class Meta:
        model = Episode
        fields = '__all__'


class EpisodeStatSerializer(serializers.ModelSerializer):
    episode = EpisodeSerializer(read_only=True)
    class Meta:
        model = EpisodeStat
        fields =  '__all__'

class CompaignSerializer(serializers.ModelSerializer):
        announcer=UserSerializer()
        class Meta:
            model = Compaign
            fields = '__all__'

class AdSerializer(serializers.ModelSerializer):
    podcast = PodcastsSerializer()
    compaign=CompaignSerializer()

    class Meta:
        model = Ad
        fields = '__all__'

class PodcastStatsGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastStatGeneral
        fields = '__all__'

class PodcastPlaysSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    plays = serializers.IntegerField(read_only=True)
