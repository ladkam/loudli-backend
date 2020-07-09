from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Tag,Podcast,Gender,CompaignAttachedFile,UserProfileInfo,Compaign,EpisodeStat,PodcastStatGeneral,Episode,Message,AgeGroup,Education,Country,City,Interest
from django.db.models import Q

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
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
        fields ='__all__'

class PodcastsSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )
    city = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )
    country = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )
    class Meta:
        model = Podcast
        fields = '__all__'

class PodcastsSerializerPost(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    city = serializers.SlugRelatedField(
        slug_field='name',
        many=True,
        queryset = City.objects.all())
    country=serializers.SlugRelatedField(
        slug_field='name',
        many=True,
        queryset=Country.objects.all())

    class Meta:
        model = Podcast
        fields = '__all__'

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        city_data = validated_data.pop('city')
        country_data = validated_data.pop('country')

        podcast = Podcast.objects.create(**validated_data)
        for tag in tags_data:
            name = tag.get("name")
            tag, created = Tag.objects.filter(
                Q(name=name)
            ).get_or_create(name=name)
            podcast.tags.add(tag)

        for city in city_data:
            podcast.city.add(city)
        for country in country_data:
            podcast.country.add(country)

        podcast.save()
        return podcast

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

class CompaignAttachedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompaignAttachedFile
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
    targetGender = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
     )
    ageGroup = AgeGroupSerializer(read_only=True, many=True)
    educationLevel = EducationSerializer(read_only=True, many=True)
    genderSerializer = GenderSerializer(read_only=True, many=True)
    CompaignAttachedFile =  CompaignAttachedFileSerializer(many=True,read_only=True)
    class Meta:
        model = Compaign
        fields = '__all__'

    def get_message_set(self, instance):
        messages = instance.message_set.all().order_by('sendDate')
        return MessageSerializer(messages, many=True).data


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        return token