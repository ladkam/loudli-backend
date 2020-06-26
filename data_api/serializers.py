from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Podcast,Gender,UserProfileInfo,Ad,Compaign,EpisodeStat,PodcastStatGeneral,Episode,Message,AgeGroup,Education,Country,City,Interest


class UserProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileInfo
        fields = '__all__'

class UserProfileInfoGetSerializer(serializers.ModelSerializer):
    #user = UserSerializer(read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = UserProfileInfo
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    UserProfileInfo = UserProfileInfoSerializer(partial=True, required=True,source='profile')
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','id','UserProfileInfo']

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

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'


"""
class AdSerializer(serializers.ModelSerializer):
    podcast = PodcastsSerializer()
    compaign=CompaignSerializer()
    class Meta:
        model = Ad
        fields = '__all__'
"""

class PodcastStatsGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastStatGeneral
        fields = '__all__'

class PodcastPlaysSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    plays = serializers.IntegerField(read_only=True)


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model = Message
        fields = '__all__'



class MessageOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'



class AgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class CompaignSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Compaign
        fields = '__all__'


class CompaignSerializer(serializers.ModelSerializer):
    announcer = UserSerializer()
    podcast = PodcastsSerializer()
    message_set = serializers.SerializerMethodField()
    country = CountrySerializer(read_only=True, many=True)
    interests = InterestSerializer(read_only=True, many=True)
    city = CitySerializer(read_only=True, many=True)
    ageGroup = AgeGroupSerializer(read_only=True, many=True)
    educationLevel = EducationSerializer(read_only=True, many=True)
    genderSerializer = GenderSerializer(read_only=True, many=True)

    class Meta:
        model = Compaign
        fields = '__all__'

    def get_message_set(self, instance):
        messages = instance.message_set.all().order_by('sendDate')
        return MessageSerializer(messages, many=True).data

class AdSerializer(serializers.ModelSerializer):
    podcast = PodcastsSerializer()
    compaign=CompaignSerializer()
    class Meta:
        model = Ad
        fields = '__all__'