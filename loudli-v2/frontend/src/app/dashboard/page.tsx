'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import {
  Mic2,
  TrendingUp,
  MessageSquare,
  Plus,
  ArrowRight,
  Clock,
  DollarSign,
  Eye,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { useAuthStore } from '@/lib/store'
import { podcastsApi, campaignsApi } from '@/lib/api'
import { formatCurrency, getStatusColor } from '@/lib/utils'

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuthStore()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted && !authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [mounted, authLoading, isAuthenticated, router])

  const isPodcaster = user?.profile?.user_type === 'podcaster'

  const { data: myPodcasts, isLoading: podcastsLoading } = useQuery({
    queryKey: ['myPodcasts'],
    queryFn: podcastsApi.getMyPodcasts,
    enabled: isAuthenticated && isPodcaster,
  })

  const { data: campaigns, isLoading: campaignsLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.list({ limit: 5 }),
    enabled: isAuthenticated,
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['campaignStats'],
    queryFn: campaignsApi.getStats,
    enabled: isAuthenticated,
  })

  if (!mounted || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.profile?.first_name || user?.email}
        </h1>
        <p className="text-gray-500 mt-1">
          Here's what's happening with your {isPodcaster ? 'podcasts' : 'campaigns'}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 rounded-lg">
                {isPodcaster ? (
                  <Mic2 className="h-6 w-6 text-primary-600" />
                ) : (
                  <TrendingUp className="h-6 w-6 text-primary-600" />
                )}
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">
                  {isPodcaster ? 'Your Podcasts' : 'Active Campaigns'}
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {isPodcaster ? myPodcasts?.length || 0 : stats?.active_campaigns || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Budget</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(stats?.total_budget || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Eye className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Impressions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats?.total_impressions?.toLocaleString() || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <MessageSquare className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats?.total_campaigns || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Podcasts Section (for podcasters) */}
        {isPodcaster && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Your Podcasts</h2>
              <Link href="/dashboard/podcasts/new">
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  Add Podcast
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {podcastsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : myPodcasts?.length === 0 ? (
                <div className="text-center py-8">
                  <Mic2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">You haven't added any podcasts yet</p>
                  <Link href="/dashboard/podcasts/new">
                    <Button>Add Your First Podcast</Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {myPodcasts?.slice(0, 5).map((podcast) => (
                    <Link
                      key={podcast.id}
                      href={`/podcasts/${podcast.id}`}
                      className="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center">
                        <Mic2 className="h-6 w-6 text-gray-400" />
                      </div>
                      <div className="ml-4 flex-1">
                        <h3 className="font-medium text-gray-900">{podcast.title}</h3>
                        <p className="text-sm text-gray-500">
                          {podcast.total_episodes} episodes
                        </p>
                      </div>
                      <ArrowRight className="h-5 w-5 text-gray-400" />
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Browse Podcasts (for advertisers) */}
        {!isPodcaster && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Find Podcasts</h2>
              <Link href="/podcasts">
                <Button size="sm" variant="outline">
                  Browse All
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Mic2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4">
                  Discover podcasts to advertise on
                </p>
                <Link href="/podcasts">
                  <Button>Browse Podcasts</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recent Campaigns */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Recent Campaigns</h2>
            <Link href="/dashboard/campaigns">
              <Button size="sm" variant="outline">
                View All
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {campaignsLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : campaigns?.length === 0 ? (
              <div className="text-center py-8">
                <TrendingUp className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No campaigns yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {campaigns?.map((campaign) => (
                  <Link
                    key={campaign.id}
                    href={`/dashboard/campaigns/${campaign.id}`}
                    className="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{campaign.title}</h3>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{new Date(campaign.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        campaign.status
                      )}`}
                    >
                      {campaign.status.replace('_', ' ')}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
