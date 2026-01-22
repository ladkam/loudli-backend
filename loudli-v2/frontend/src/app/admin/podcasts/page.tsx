'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Mic2, Eye, EyeOff } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { adminApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function AdminPodcastsPage() {
  const queryClient = useQueryClient()

  const { data: podcasts, isLoading } = useQuery({
    queryKey: ['adminPodcasts'],
    queryFn: () => adminApi.getAllPodcasts({ limit: 100 }),
  })

  const toggleActiveMutation = useMutation({
    mutationFn: adminApi.togglePodcastActive,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminPodcasts'] })
    },
  })

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Podcast Management</h1>
        <p className="text-gray-500 mt-1">View and manage all podcasts on the platform</p>
      </div>

      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">All Podcasts ({podcasts?.length || 0})</h2>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : podcasts?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Mic2 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p>No podcasts yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Podcast
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Owner
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Episodes
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Created
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {podcasts?.map((podcast: any) => (
                    <tr key={podcast.id} className="hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center mr-3">
                            <Mic2 className="h-5 w-5 text-primary-600" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{podcast.title}</div>
                            {podcast.author && (
                              <div className="text-sm text-gray-500">by {podcast.author}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {podcast.owner_email}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {podcast.total_episodes}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            podcast.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {podcast.is_active ? 'Active' : 'Hidden'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-500">
                        {formatDate(podcast.created_at)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant={podcast.is_active ? 'outline' : 'primary'}
                            onClick={() => toggleActiveMutation.mutate(podcast.id)}
                            title={podcast.is_active ? 'Hide podcast' : 'Show podcast'}
                          >
                            {podcast.is_active ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                          <a href={`/podcasts/${podcast.id}`} target="_blank">
                            <Button size="sm" variant="ghost">
                              View
                            </Button>
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
