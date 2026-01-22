'use client'

import { useQuery } from '@tanstack/react-query'
import { TrendingUp } from 'lucide-react'
import { PodcastCard } from '@/components/podcast/PodcastCard'
import { podcastsApi } from '@/lib/api'

export default function TrendingPage() {
  const { data: trendingPodcasts, isLoading, error } = useQuery({
    queryKey: ['trendingPodcasts'],
    queryFn: () => podcastsApi.getTrending(20),
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary-100 rounded-lg">
            <TrendingUp className="h-6 w-6 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Trending Podcasts</h1>
        </div>
        <p className="text-gray-600">
          Discover the most popular podcasts right now
        </p>
      </div>

      {/* Error State */}
      {error && (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">Unable to load trending podcasts</p>
          <p className="text-gray-400 mt-2">
            The Podcast Index API may not be configured. Check your environment variables.
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="aspect-square bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      {/* Podcast Grid */}
      {trendingPodcasts && trendingPodcasts.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {trendingPodcasts.map((podcast, index) => (
            <div key={podcast.id} className="relative">
              {index < 3 && (
                <div className="absolute -top-2 -left-2 z-10 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm shadow-lg">
                  {index + 1}
                </div>
              )}
              <PodcastCard podcast={podcast} />
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && trendingPodcasts?.length === 0 && (
        <div className="text-center py-16">
          <TrendingUp className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No trending podcasts available</p>
        </div>
      )}
    </div>
  )
}
