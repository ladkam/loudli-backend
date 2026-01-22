'use client'

import { use } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import {
  Mic2,
  Globe,
  Rss,
  Calendar,
  Clock,
  Play,
  ExternalLink,
  MessageSquare,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { podcastsApi } from '@/lib/api'
import { formatDuration, formatDate } from '@/lib/utils'
import { useAuthStore } from '@/lib/store'

interface PageProps {
  params: Promise<{ id: string }>
}

export default function PodcastDetailPage({ params }: PageProps) {
  const { id } = use(params)
  const { isAuthenticated, user } = useAuthStore()
  const isAdvertiser = user?.profile?.user_type === 'advertiser'

  const { data: podcast, isLoading } = useQuery({
    queryKey: ['podcast', id],
    queryFn: () => podcastsApi.get(parseInt(id)),
  })

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="flex flex-col md:flex-row gap-8 mb-8">
            <div className="w-64 h-64 bg-gray-200 rounded-xl" />
            <div className="flex-1 space-y-4">
              <div className="h-8 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
              <div className="h-20 bg-gray-200 rounded" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!podcast) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-16">
          <Mic2 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Podcast not found</h2>
          <Link href="/podcasts">
            <Button>Browse Podcasts</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row gap-8 mb-8">
        {/* Podcast Cover */}
        <div className="relative w-64 h-64 flex-shrink-0 rounded-xl overflow-hidden bg-gray-100 shadow-lg">
          {podcast.cover_image_url ? (
            <Image
              src={podcast.cover_image_url}
              alt={podcast.title}
              fill
              className="object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Mic2 className="h-24 w-24 text-gray-400" />
            </div>
          )}
        </div>

        {/* Podcast Info */}
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{podcast.title}</h1>
          <p className="text-lg text-gray-600 mb-4">{podcast.author || 'Unknown author'}</p>

          {podcast.description && (
            <p className="text-gray-600 mb-6 line-clamp-3">{podcast.description}</p>
          )}

          {/* Stats */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center text-gray-500">
              <Mic2 className="h-5 w-5 mr-2" />
              <span>{podcast.total_episodes} episodes</span>
            </div>
            {podcast.language && (
              <div className="flex items-center text-gray-500">
                <Globe className="h-5 w-5 mr-2" />
                <span>{podcast.language.toUpperCase()}</span>
              </div>
            )}
            {podcast.last_rss_sync && (
              <div className="flex items-center text-gray-500">
                <Calendar className="h-5 w-5 mr-2" />
                <span>Updated {formatDate(podcast.last_rss_sync)}</span>
              </div>
            )}
          </div>

          {/* Categories */}
          {podcast.categories.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {podcast.categories.map((category) => (
                <span
                  key={category.id}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {category.name}
                </span>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            {podcast.website_url && (
              <a href={podcast.website_url} target="_blank" rel="noopener noreferrer">
                <Button variant="outline">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Visit Website
                </Button>
              </a>
            )}
            {podcast.rss_feed_url && (
              <a href={podcast.rss_feed_url} target="_blank" rel="noopener noreferrer">
                <Button variant="outline">
                  <Rss className="h-4 w-4 mr-2" />
                  RSS Feed
                </Button>
              </a>
            )}
            {isAuthenticated && isAdvertiser && (
              <Link href={`/dashboard/campaigns/new?podcast=${podcast.id}`}>
                <Button>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Start Campaign
                </Button>
              </Link>
            )}
            {!isAuthenticated && (
              <Link href="/register?type=advertiser">
                <Button>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Advertise on This Podcast
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Episodes Section */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold text-gray-900">
            Episodes ({podcast.episodes?.length || 0})
          </h2>
        </CardHeader>
        <CardContent>
          {!podcast.episodes || podcast.episodes.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No episodes available
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {podcast.episodes.map((episode) => (
                <div key={episode.id} className="py-4 first:pt-0 last:pb-0">
                  <div className="flex items-start gap-4">
                    <button className="flex-shrink-0 w-10 h-10 rounded-full bg-primary-100 hover:bg-primary-200 flex items-center justify-center transition-colors">
                      <Play className="h-5 w-5 text-primary-600 ml-0.5" />
                    </button>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 mb-1 line-clamp-1">
                        {episode.title}
                      </h3>
                      {episode.description && (
                        <p className="text-sm text-gray-500 line-clamp-2 mb-2">
                          {episode.description}
                        </p>
                      )}
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        {episode.published_at && (
                          <span className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {formatDate(episode.published_at)}
                          </span>
                        )}
                        {episode.duration_seconds && (
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {formatDuration(episode.duration_seconds)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
