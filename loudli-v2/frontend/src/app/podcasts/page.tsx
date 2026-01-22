'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { PodcastCard } from '@/components/podcast/PodcastCard'
import { podcastsApi } from '@/lib/api'

export default function PodcastsPage() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  const { data: podcasts, isLoading } = useQuery({
    queryKey: ['podcasts', debouncedSearch],
    queryFn: () => podcastsApi.list({ search: debouncedSearch || undefined, limit: 50 }),
  })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: podcastsApi.getCategories,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setDebouncedSearch(search)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Browse Podcasts</h1>
        <p className="text-gray-600">
          Discover amazing podcasts to sponsor and reach engaged audiences
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              placeholder="Search podcasts..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button type="submit">Search</Button>
        </form>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Categories */}
      {categories && categories.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-8">
          <Button variant="secondary" size="sm" className="rounded-full">
            All
          </Button>
          {categories.slice(0, 10).map((category) => (
            <Button
              key={category.id}
              variant="outline"
              size="sm"
              className="rounded-full"
            >
              {category.name}
            </Button>
          ))}
        </div>
      )}

      {/* Podcast Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="aspect-square bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : podcasts?.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">No podcasts found</p>
          <p className="text-gray-400 mt-2">Try adjusting your search terms</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {podcasts?.map((podcast) => (
            <PodcastCard key={podcast.id} podcast={podcast} />
          ))}
        </div>
      )}
    </div>
  )
}
