from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from django.db.models import Sum
from .serializers import UserSerializer,\
    GroupSerializer,PodcastPlaysSerializer,PodcastsSerializer,PodcastsSerializerPost,\
    UserProfileInfoSerializer,AdSerializer,CompaignSerializer,EpisodeStatSerializer,\
    PodcastStatsGeneralSerializer,CompaignSerializerPost,EpisodeImportedSerializer,EpisodeStat,EpisodeSerializer,MessageSerializer,MessageOnlySerializer,UserProfileInfoGetSerializer,AgeGroupSerializer\
    ,EducationSerializer,CountrySerializer,CitySerializer,InterestSerializer,GenderSerializer,CompaignFilesSerializer
from rest_framework import generics
from .models import Podcast,UserProfileInfo,CompaignFiles,Gender,Ad,Compaign,PodcastStatGeneral,EpisodeImported,Episode,EpisodeStat,Message,AgeGroup,Education,Country,City,Interest
from rest_framework.views import APIView
from rest_framework.response import Response
from scrape_podcast_data import AnchorScraper,listennotesData
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

import logging

logger = logging.getLogger('analyzer')

"""
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    """

class UserProfileInfoList(generics.ListCreateAPIView):
    queryset = UserProfileInfo.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserProfileInfoSerializer
        if self.request.method == 'GET':
            return UserProfileInfoGetSerializer
    def get_queryset(self):
        user = self.request.user
        return UserProfileInfo.objects.filter(user=user.id)

class PodcastsList(generics.ListCreateAPIView):
    queryset = Podcast.objects.all()
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PodcastsSerializerPost
        if self.request.method == 'GET':
            return PodcastsSerializer

class PodcastsListFilter(generics.ListCreateAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastsSerializer

    def get_queryset(self):
        user = self.request.user
        return Podcast.objects.filter(author=user.id)


class PodcastsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastsSerializer

class UserProfileInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfileInfo.objects.all()
    serializer_class = UserProfileInfoSerializer
    def get_queryset(self):
        user = self.request.user
        return UserProfileInfo.objects.filter(user=user.id)


class AdList(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    def get_queryset(self):
        user = self.request.user
        querytype=self.request.GET.get('type','')

        if querytype=='podcaster':
            return Ad.objects.filter(podcast__author=user.id)
        if querytype == 'announcer':
            return Ad.objects.filter(compaign__announcer=user.id)

    filterset_fields = ['podcast', 'compaign']

class AdDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

class AgeGroupList(generics.ListAPIView):
    queryset = AgeGroup.objects.all()
    serializer_class = AgeGroupSerializer

class CountryList(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CityList(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class InterestList(generics.ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer

class EducationList(generics.ListAPIView):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

class CompaignFilesList(generics.ListAPIView):
    queryset = CompaignFiles.objects.all()
    serializer_class = CompaignFilesSerializer

class CompaignList(generics.ListCreateAPIView):
    queryset = Compaign.objects.all()


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompaignSerializerPost
        if self.request.method == 'GET':
            return CompaignSerializer

    def get_queryset(self):
        user = self.request.user
        userType = UserProfileInfo.objects.get(user = user.id).type
        if userType == 'podcaster':
            return Compaign.objects.filter(podcast__author=user.id)
        else:
            return Compaign.objects.filter(announcer=user.id)

"""
    def post(self, request, *args, **kwargs):
        if not self.request.POST._mutable:
            self.request.POST._mutable = True
        self.request.data.update({"educationLevel": [int(el) for el in self.request.data['educationLevellab'].split('L')]})
        self.request.data.update({"city": [int(el) for el in self.request.data['citylab'].split('L')]})
        self.request.data.update({"country": [int(el) for el in self.request.data['countrylab'].split('L')]})
        self.request.data.update({"interests": [int(el) for el in self.request.data['interestslab'].split('L')]})
        self.request.data.update({"ageGroup": [int(el) for el in self.request.data['ageGrouplab'].split('L')]})


        logger.warning(request.data)


        serializer = CompaignSerializerPost(data=request.data)
        if serializer.is_valid():
            Compaign = serializer.save()
            serializer = CompaignSerializerPost(Compaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
"""


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name':user.first_name,
            'last_name': user.last_name
        })



class CompaignDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Compaign.objects.all()
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            print(self.request.data)
            return CompaignSerializerPost
        if self.request.method == 'GET':
            return CompaignSerializer

### new comment

class PodcastatList(APIView):

    def get(self, request, format=None):
        podcast = self.request.GET.get('podcast', '')
        if(podcast):
            stats = EpisodeStat.objects.filter(episode__podcast=podcast)
        else:
            stats = EpisodeStat.objects.all()
        serializer = EpisodeStatSerializer(stats, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        podcastId = request.data.__getitem__('podcast')
        logger.warning("Recieved request to add data to podcast "+request.data.__getitem__('podcast'))
        PodcastToAdd = Podcast.objects.get(pk=request.data.__getitem__('podcast'))
        setattr(PodcastToAdd, 'episodesLoadingStatus', 'Started')
        PodcastToAdd.save()
        logger.info('changed status of podcast Episode loading of podcast ')
        stats=[]

        with AnchorScraper(podcast=request.data.__getitem__('podcast'),username=request.data.__getitem__('username'),password=request.data.__getitem__('password')) as Anchor:
            df = Anchor.scrape()
            if len(df)==0:
                setattr(PodcastToAdd, 'episodesLoadingStatus', 'Login Failed')
                PodcastToAdd.save()
                return Response({'login error'}, status=status.HTTP_400_BAD_REQUEST)
            nbEpisodes = len(df['episode'].unique())
            logger.info('data receieved' + str(len(df)) + 'lines fetched')
            plays=df['Plays'].sum()
            _, created = PodcastStatGeneral.objects.get_or_create(
                plays=plays,
                nbEpisodes=nbEpisodes,
                podcast=PodcastToAdd
            )
            episodeOld = Episode.objects.filter(podcast=podcastId)
            if len(episodeOld) > 0:
                episodeOld.delete()
            for episode in df['episode'].unique():
                episodeCreated, created = EpisodeImported.objects.get_or_create(
                    name= episode,
                    podcast= PodcastToAdd
                )
                EpisodeToAdd = EpisodeImported.objects.get(pk=episodeCreated.id)
                logger.info('importing episodes')
                episodeData = df[df['episode']== episode]
                EpisodeStatsOld = EpisodeStat.objects.filter(episode__podcast=podcastId)
                if len(EpisodeStatsOld)>0:
                    EpisodeStatsOld.delete()
                for index, row in episodeData.iterrows():
                    stat, created = EpisodeStat.objects.get_or_create(
                        date = row['Time (UTC)'],
                        plays = row['Plays'],
                        episode = EpisodeToAdd
                    )
                stats.append(stat.id)
            EpisodeStatData = EpisodeStat.objects.filter(pk__in=stats)
            serializer = EpisodeStatSerializer(EpisodeStatData, many=True)
            logger.info('sending ok')
            setattr(PodcastToAdd, 'episodesLoadingStatus', 'Ok')
            PodcastToAdd.save()
            logger.info('changed status of podcast Episode loading')
            return Response({'Data Loaded'}, status=status.HTTP_200_OK)


class EpisodeList(APIView):
    def post(self, request, format=None):
        podcastFilter = Podcast.objects.get(pk=request.data.__getitem__('podcast'))
        EpisodesList = Episode.objects.filter(podcast=podcastFilter)
        serializer = EpisodeSerializer(EpisodesList, many=True)
        return Response(serializer.data)


class UpdatePodcastEpisodes(APIView):
    def post(self,request):
        podcastId = request.data.__getitem__('podcastId')
        episodesToUpdate = listennotesData.podcast(podcastId)
        episodesToUpdate.update_episodes()
        content = {'Sucess'}
        return Response(content, status=status.HTTP_201_CREATED)


class PodcastStatsGeneral(generics.ListCreateAPIView):
    """
    queryset = PodcastStatGeneral.objects.all()
    serializer_class = PodcastStatsGeneralSerializer
    """
    def get(self,request):
        user = self.request.user
        podcasts=Podcast.objects.filter(author=user.id)
        nb_episodes =sum([p.nb_episodes for p in podcasts])
        nb_podcasts = len(podcasts)
        episodes=EpisodeStat.objects.filter(episode__podcast__author=user.id)
        nb_plays = sum([e.plays for e in episodes])


        return Response({'nb_episodes':nb_episodes,'nb_podcasts':nb_podcasts,'nb_plays':nb_plays})

class PodcastPlays(APIView):
    def get(self,request):
        podcast = self.request.GET.get('podcast', '')
        logger.info('requested info about ' +  podcast)
        if(podcast):
            Podcaststats = EpisodeStat.objects.filter(episode__podcast=podcast).values('date').annotate(played=Sum('plays')).order_by('date')
            return Response(Podcaststats)
        else:
            return Response({'no plays for podcast'+podcast}, status=status.HTTP_400_BAD_REQUEST)

class MessagesList(generics.ListCreateAPIView):

    queryset = Message.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageOnlySerializer
        if self.request.method == 'GET':
            return MessageSerializer

    def get_queryset(self):
        user = self.request.user
        if len(Message.objects.filter(sender=user.id)) != 0:
            return Message.objects.filter(sender=user.id)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer