'use client'

import { useQuery } from '@tanstack/react-query'
import { Users, Mic2, TrendingUp, Link2 } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { adminApi } from '@/lib/api'

export default function AdminDashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['adminStats'],
    queryFn: adminApi.getStats,
  })

  const statCards = [
    {
      label: 'Total Users',
      value: stats?.total_users || 0,
      icon: Users,
      color: 'bg-blue-100 text-blue-600',
      subtext: `${stats?.total_podcasters || 0} podcasters, ${stats?.total_advertisers || 0} advertisers`,
    },
    {
      label: 'Total Podcasts',
      value: stats?.total_podcasts || 0,
      icon: Mic2,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      label: 'Campaigns',
      value: stats?.total_campaigns || 0,
      icon: TrendingUp,
      color: 'bg-green-100 text-green-600',
      subtext: `${stats?.active_campaigns || 0} active`,
    },
    {
      label: 'Matches',
      value: stats?.total_matches || 0,
      icon: Link2,
      color: 'bg-orange-100 text-orange-600',
      subtext: `${stats?.pending_matches || 0} pending`,
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of platform statistics</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-3">
                  <div className="h-10 w-10 bg-gray-200 rounded-lg" />
                  <div className="h-8 bg-gray-200 rounded w-20" />
                  <div className="h-4 bg-gray-200 rounded w-32" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat) => (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <div className={`inline-flex p-3 rounded-lg ${stat.color} mb-4`}>
                  <stat.icon className="h-6 w-6" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {stat.value.toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">{stat.label}</div>
                {stat.subtext && (
                  <div className="text-xs text-gray-400 mt-1">{stat.subtext}</div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Quick Actions</h2>
          </CardHeader>
          <CardContent className="space-y-3">
            <a
              href="/admin/settings"
              className="block p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className="font-medium text-gray-900">Configure API Keys</div>
              <div className="text-sm text-gray-500">
                Set up Podcast Index API for trending & search
              </div>
            </a>
            <a
              href="/admin/matches"
              className="block p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className="font-medium text-gray-900">Create Matches</div>
              <div className="text-sm text-gray-500">
                Connect podcasters with advertisers
              </div>
            </a>
            <a
              href="/admin/users"
              className="block p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className="font-medium text-gray-900">Manage Users</div>
              <div className="text-sm text-gray-500">
                View and manage platform users
              </div>
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Getting Started</h2>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3 text-sm">
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-medium mr-3">
                  1
                </span>
                <div>
                  <div className="font-medium text-gray-900">Add API Keys</div>
                  <div className="text-gray-500">
                    Get free keys from{' '}
                    <a
                      href="https://podcastindex.org/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:underline"
                    >
                      podcastindex.org
                    </a>
                  </div>
                </div>
              </li>
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-medium mr-3">
                  2
                </span>
                <div>
                  <div className="font-medium text-gray-900">Import Podcasts</div>
                  <div className="text-gray-500">
                    Users can import from RSS feeds or search
                  </div>
                </div>
              </li>
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-medium mr-3">
                  3
                </span>
                <div>
                  <div className="font-medium text-gray-900">Create Matches</div>
                  <div className="text-gray-500">
                    Connect podcasters with relevant advertisers
                  </div>
                </div>
              </li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
