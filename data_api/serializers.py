from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Plays,Ep,CompaignStatus,Tag,Podcast,Gender, Date,Audio,attached,Proposition,UserProfileInfo,Compaign,EpisodeStat,PodcastStatGeneral,Episode,Message,AgeGroup,Education,Country,City,Interest
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError
import logging
import boto3
from botocore.exceptions import ClientError


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

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
        fields = ['first_name','last_name','id','UserProfileInfo']

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
    targetGender = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )
    ageGroup = serializers.SlugRelatedField(
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

    country = serializers.SlugRelatedField(
        slug_field='name',
        many=True,
        queryset=Country.objects.all())

    ageGroup = serializers.SlugRelatedField(
        slug_field='name',
        many=True,
        queryset = AgeGroup.objects.all()
    )

    class Meta:
        model = Podcast
        fields = '__all__'

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        city_data = validated_data.pop('city')
        country_data = validated_data.pop('country')
        ageGroup_data = validated_data.pop('ageGroup')

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

        for ageGroup in ageGroup_data:
            podcast.ageGroup.add(ageGroup)

        podcast.save()
        return podcast

class EpisodesSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Ep
        fields='__all__'


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ep
        fields='__all__'

class EpisodeImportedSerializer(serializers.ModelSerializer):
    podcast = PodcastsSerializerPost(read_only=True)
    class Meta:
        model = Episode
        fields = '__all__'

class EpisodeStatSerializer(serializers.ModelSerializer):
    episode = EpisodesSerializer(read_only=True)
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


class PodcastStatsGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastStatGeneral
        fields = '__all__'

class PodcastPlaysSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    plays = serializers.IntegerField(read_only=True)

class attachedSerializer(serializers.ModelSerializer):
    class Meta:
        model = attached
        fields = '__all__'

class PropositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposition
        fields = '__all__'

class PropositionSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Proposition
        fields = '__all__'

class MessageSerializerOnly(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
    def create(self,validated_data):
        message = Message.objects.create(**validated_data)
        compaignId = message.compaign.id
        compaign = Compaign.objects.get(id=compaignId)
        print(compaign.podcast.author.id)
        messageFor = compaign.podcast.author if compaign.podcast.author!=compaign.messageFor else compaign.announcer
        setattr(compaign,'messageFor',messageFor)
        compaign.save()
        return message

class PlaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plays
        fields = '__all__'

class MessageSerializerPlays(serializers.ModelSerializer):
    plays = PlaysSerializer()
    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        Plays_data = validated_data.pop('plays')
        message = Message.objects.create(**validated_data)
        oldPlays = Plays.objects.filter(message__compaign=message.compaign,status='current')
        for plays in oldPlays:
            setattr(plays,'status','previous')
            plays.save()
        plays = Plays.objects.create(message=message, **Plays_data)
        compaign = Compaign.objects.get(id=message.compaign.id)
        #actionFor = compaign.podcast.author if compaign.podcast.author != self.context['request'].user else compaign.announcer
        #setattr(compaign, 'actionFor', actionFor)
        setattr(compaign, 'advancement', plays.number)
        compaign.save()

        return message


class MessageSerializerPropositions(serializers.ModelSerializer):
    proposition = PropositionSerializer()
    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        proposition_data = validated_data.pop('proposition')
        message = Message.objects.create(**validated_data)
        oldPropositions = Proposition.objects.filter(message__compaign=message.compaign,status='pending')
        for proposition in oldPropositions:
            setattr(proposition,'status','refused')
            proposition.save()
        proposition = Proposition.objects.create(message=message, **proposition_data)
        compaign = Compaign.objects.get(id=message.compaign.id)
        actionFor = compaign.podcast.author if compaign.podcast.author != self.context['request'].user else compaign.announcer
        setattr(compaign, 'actionFor', actionFor)
        setattr(compaign,'startedExchange',True)
        compaign.save()

        return message



class CompaignSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Compaign
        exclude = ('status', )

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = '__all__'

class CompaignStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=CompaignStatus
        fields='__all__'

class DatePublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Date
        fields = '__all__'

class MessageSerializerDatePublication(serializers.ModelSerializer):
    date = DatePublicationSerializer()
    print('here')
    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        print('là')

        DatePublication_data = validated_data.pop('date')
        message = Message.objects.create(**validated_data)
        oldDates = Date.objects.filter(message__compaign=message.compaign, status='pending')
        for oldDate in oldDates:
            setattr(oldDate, 'status', 'refused')
            oldDate.save()

        date = Date.objects.create(message=message, **DatePublication_data)
        compaign = Compaign.objects.get(id=message.compaign.id)
        actionFor = compaign.announcer
        setattr(compaign, 'actionFor', actionFor)
        setattr(compaign,'startedExchange',True)

        compaign.save()
        print('ici')
        print(date)
        return message

class MessageSerializerAudio(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = '__all__'
    def create(self, validated_data):
        initData = dict(self.initial_data)
        sender = User.objects.get(id=int(initData['sender'][0]))
        compaign = Compaign.objects.get(id=int(initData['compaign'][0]))
        message = Message.objects.create(text=initData['text'][0],type='Enregistrement',sender=sender,compaign=compaign)
        oldAudio = Audio.objects.filter(message__compaign=message.compaign, status='pending')
        for audio in oldAudio:
            setattr(audio, 'status', 'refused')
            audio.save()
        audio = Audio.objects.create(**validated_data,message=message)
        setattr(compaign, 'actionFor', compaign.announcer)
        compaign.save()
        return audio

class MessageSerializer(serializers.ModelSerializer):
    #sender = UserSerializer()
    plays = PlaysSerializer()
    audio = AudioSerializer()
    proposition = PropositionSerializer()
    date = DatePublicationSerializer()
    class Meta:
        model = Message
        fields = '__all__'



class CompaignSerializer(serializers.ModelSerializer):
    announcer = UserSerializer()
    ep = EpisodeSerializer(many=True)
    #audioFile_set =  serializers.SerializerMethodField()
    ##proposition_set = serializers.SerializerMethodField()
    podcast = PodcastsSerializer()
    message_set = serializers.SerializerMethodField()
    status = serializers.SlugRelatedField(read_only=True,slug_field='name')

    targetGender = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    country = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    city = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    ageGroup = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    attached_set = serializers.SerializerMethodField()

    class Meta:
        model = Compaign
        fields = '__all__'

    def get_message_set(self, instance):
        messages = instance.message_set.all().order_by('sendDate')
        return MessageSerializer(messages, many=True).data
    def get_episodes_set(self, instance):
        episodes = instance.episodes_set.all()
        return EpisodeSerializer(episodes, many=True).data
    ##def get_proposition_set(self, instance):
      ##  propositions = instance.proposition_set.all().order_by('date')
       ## return PropositionSerializer(propositions, many=True).data
    """def get_audioFile(self, obj):
        if obj.audioFileName:
            return create_presigned_url('loudli-files','campaign_'+str(obj.id)+'_'+obj.audioFileName)
        else:
            return 'coco'
            """
    def get_attached_set(self,instance):
        files = instance.attached_set.all()
        return attachedSerializer(files, many=True).data



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