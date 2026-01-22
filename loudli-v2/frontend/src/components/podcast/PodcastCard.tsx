'use client'

import Image from 'next/image'
import Link from 'next/link'
import { Mic2, Headphones } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { truncateText } from '@/lib/utils'
import type { Podcast, PodcastSearchResult } from '@/types'

interface PodcastCardProps {
  podcast: Podcast | PodcastSearchResult
  variant?: 'default' | 'compact'
}

export function PodcastCard({ podcast, variant = 'default' }: PodcastCardProps) {
  const imageUrl = 'cover_image_url' in podcast ? podcast.cover_image_url : podcast.image_url
  const episodeCount = 'total_episodes' in podcast ? podcast.total_episodes : podcast.episode_count
  const podcastId = podcast.id

  if (variant === 'compact') {
    return (
      <Link href={`/podcasts/${podcastId}`}>
        <Card className="flex items-center p-3 hover:shadow-md transition-shadow cursor-pointer">
          <div className="relative w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
            {imageUrl ? (
              <Image src={imageUrl} alt={podcast.title} fill className="object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Mic2 className="h-8 w-8 text-gray-400" />
              </div>
            )}
          </div>
          <div className="ml-4 flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">{podcast.title}</h3>
            <p className="text-sm text-gray-500 truncate">{podcast.author || 'Unknown author'}</p>
          </div>
        </Card>
      </Link>
    )
  }

  return (
    <Link href={`/podcasts/${podcastId}`}>
      <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer h-full flex flex-col">
        <div className="relative aspect-square bg-gray-100">
          {imageUrl ? (
            <Image src={imageUrl} alt={podcast.title} fill className="object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Mic2 className="h-16 w-16 text-gray-400" />
            </div>
          )}
        </div>
        <div className="p-4 flex-1 flex flex-col">
          <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1">{podcast.title}</h3>
          <p className="text-sm text-gray-500 mb-2">{podcast.author || 'Unknown author'}</p>
          {podcast.description && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-3">
              {truncateText(podcast.description, 100)}
            </p>
          )}
          <div className="mt-auto flex items-center text-sm text-gray-500">
            <Headphones className="h-4 w-4 mr-1" />
            <span>{episodeCount || 0} episodes</span>
          </div>
        </div>
      </Card>
    </Link>
  )
}
