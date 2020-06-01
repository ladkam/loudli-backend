from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from django.db.models import Sum
from .serializers import UserSerializer,\
    GroupSerializer,PodcastPlaysSerializer,PodcastsSerializer,PodcastsSerializerPost,\
    UserProfileInfoSerializer,AdSerializer,CompaignSerializer,EpisodeStatSerializer,\
    PodcastStatsGeneralSerializer,EpisodeImportedSerializer,EpisodeStat,EpisodeSerializer
from rest_framework import generics
from .models import Podcast,UserProfileInfo,Ad,Compaign,PodcastStatGeneral,EpisodeImported,Episode,EpisodeStat
from rest_framework.views import APIView
from rest_framework.response import Response
from scrape_podcast_data import AnchorScraper,listennotesData
from rest_framework import status

import logging

logger = logging.getLogger('analyzer')


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = PodcastsSerializer


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
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Podcast.objects.filter(author=user.id)



class PodcastsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastsSerializer


class UserProfileInfoList(generics.ListCreateAPIView):
    queryset = UserProfileInfo.objects.all()
    serializer_class = UserProfileInfoSerializer
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return UserProfileInfo.objects.filter(user=user.id)


class UserProfileInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfileInfo.objects.all()
    serializer_class = UserProfileInfoSerializer
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return UserProfileInfo.objects.filter(user=user.id)


class AdList(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
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

class CompaignList(generics.ListCreateAPIView):
    queryset = Compaign.objects.all()
    serializer_class = CompaignSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Compaign.objects.filter(announcer=user.id)

class CompaignDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Compaign.objects.all()
    serializer_class = CompaignSerializer

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
        logger.warning("Recieved request to add data to podcast "+request.data.__getitem__('podcast'))
        PodcastToAdd = Podcast.objects.get(pk=request.data.__getitem__('podcast'))
        setattr(PodcastToAdd, 'episodesLoadingStatus', 'Started')
        logger.info('changed status of podcast Episode loading')
        stats=[]

        with AnchorScraper(podcast=request.data.__getitem__('podcast'),username=request.data.__getitem__('username'),password=request.data.__getitem__('password')) as Anchor:
            df = Anchor.scrape()
            if len(df)==0:
                setattr(PodcastToAdd, 'episodesLoadingStatus', 'Login Failed')
                return Response({'login error'}, status=status.HTTP_400_BAD_REQUEST)
            nbEpisodes = len(df['episode'].unique())
            logger.info('data receieved' + str(len(df)) + 'lines fetched')
            plays=df['Plays'].sum()
            _, created = PodcastStatGeneral.objects.get_or_create(
                plays=plays,
                nbEpisodes=nbEpisodes,
                podcast=PodcastToAdd
            )
            for episode in df['episode'].unique():
                episodeCreated, created = EpisodeImported.objects.get_or_create(
                    name= episode,
                    podcast= PodcastToAdd
                )
                EpisodeToAdd = EpisodeImported.objects.get(pk=episodeCreated.id)
                logger.info('importing episodes')
                episodeData = df[df['episode']== episode]
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


