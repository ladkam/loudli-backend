'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link2, Plus, Trash2, Check, X } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { adminApi, Match } from '@/lib/api'
import { formatDate, getStatusColor } from '@/lib/utils'

export default function AdminMatchesPage() {
  const queryClient = useQueryClient()
  const [showNewForm, setShowNewForm] = useState(false)
  const [newMatch, setNewMatch] = useState({
    podcast_id: '',
    advertiser_id: '',
    match_score: '',
    match_reason: '',
  })
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data: matches, isLoading } = useQuery({
    queryKey: ['adminMatches', statusFilter],
    queryFn: () =>
      adminApi.getMatches({
        status_filter: statusFilter || undefined,
        limit: 100,
      }),
  })

  const { data: podcasts } = useQuery({
    queryKey: ['adminPodcasts'],
    queryFn: () => adminApi.getAllPodcasts({ limit: 100 }),
  })

  const { data: users } = useQuery({
    queryKey: ['adminUsers'],
    queryFn: () => adminApi.getUsers({ user_type: 'advertiser', limit: 100 }),
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createMatch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminMatches'] })
      setShowNewForm(false)
      setNewMatch({ podcast_id: '', advertiser_id: '', match_score: '', match_reason: '' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { status: string } }) =>
      adminApi.updateMatch(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminMatches'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: adminApi.deleteMatch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminMatches'] })
    },
  })

  const handleCreate = () => {
    if (newMatch.podcast_id && newMatch.advertiser_id) {
      createMutation.mutate({
        podcast_id: parseInt(newMatch.podcast_id),
        advertiser_id: parseInt(newMatch.advertiser_id),
        match_score: newMatch.match_score ? parseFloat(newMatch.match_score) : undefined,
        match_reason: newMatch.match_reason || undefined,
      })
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Podcaster-Advertiser Matching</h1>
        <p className="text-gray-500 mt-1">
          Connect podcasters with relevant advertisers for sponsorship opportunities
        </p>
      </div>

      {/* Info Card */}
      <Card className="mb-6 border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Link2 className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900">How Matching Works</h3>
              <p className="text-sm text-blue-700 mt-1">
                Create matches between podcasts and advertisers. When a match is created,
                both parties will be notified and can start a conversation about potential
                sponsorship deals.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filters and Actions */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="sent">Sent</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
        </select>
        <div className="flex-1" />
        <Button onClick={() => setShowNewForm(!showNewForm)}>
          <Plus className="h-4 w-4 mr-1" />
          Create Match
        </Button>
      </div>

      {/* New Match Form */}
      {showNewForm && (
        <Card className="mb-6">
          <CardHeader>
            <h2 className="text-lg font-semibold">Create New Match</h2>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Podcast
                </label>
                <select
                  value={newMatch.podcast_id}
                  onChange={(e) => setNewMatch({ ...newMatch, podcast_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select a podcast...</option>
                  {podcasts?.map((podcast: any) => (
                    <option key={podcast.id} value={podcast.id}>
                      {podcast.title} ({podcast.owner_email})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Advertiser
                </label>
                <select
                  value={newMatch.advertiser_id}
                  onChange={(e) => setNewMatch({ ...newMatch, advertiser_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select an advertiser...</option>
                  {users?.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.company_name || user.email}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <Input
                label="Match Score (0-100)"
                type="number"
                min="0"
                max="100"
                placeholder="Optional: 0-100"
                value={newMatch.match_score}
                onChange={(e) => setNewMatch({ ...newMatch, match_score: e.target.value })}
              />
              <Input
                label="Match Reason"
                placeholder="Why this match makes sense..."
                value={newMatch.match_reason}
                onChange={(e) => setNewMatch({ ...newMatch, match_reason: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowNewForm(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleCreate}
                isLoading={createMutation.isPending}
                disabled={!newMatch.podcast_id || !newMatch.advertiser_id}
              >
                Create Match
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Matches List */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">Matches ({matches?.length || 0})</h2>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : matches?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Link2 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p>No matches yet</p>
              <p className="text-sm mt-1">Create your first match to connect podcasters with advertisers</p>
            </div>
          ) : (
            <div className="space-y-4">
              {matches?.map((match) => (
                <div
                  key={match.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <div className="flex-1">
                          <div className="text-sm text-gray-500">Podcast</div>
                          <div className="font-medium text-gray-900">
                            {match.podcast_title || `Podcast #${match.podcast_id}`}
                          </div>
                          {match.podcast_author && (
                            <div className="text-xs text-gray-500">by {match.podcast_author}</div>
                          )}
                        </div>
                        <div className="flex items-center justify-center px-3">
                          <Link2 className="h-5 w-5 text-gray-400" />
                        </div>
                        <div className="flex-1">
                          <div className="text-sm text-gray-500">Advertiser</div>
                          <div className="font-medium text-gray-900">
                            {match.advertiser_company || match.advertiser_email || `User #${match.advertiser_id}`}
                          </div>
                          {match.advertiser_email && match.advertiser_company && (
                            <div className="text-xs text-gray-500">{match.advertiser_email}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}>
                          {match.status}
                        </span>
                        {match.match_score !== null && (
                          <span className="text-gray-500">
                            Score: <strong>{match.match_score}</strong>/100
                          </span>
                        )}
                        <span className="text-gray-400">
                          Created {formatDate(match.created_at)}
                        </span>
                      </div>
                      {match.match_reason && (
                        <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                          {match.match_reason}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {match.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              updateMutation.mutate({ id: match.id, data: { status: 'sent' } })
                            }
                            title="Mark as sent"
                          >
                            Send
                          </Button>
                        </>
                      )}
                      {match.status === 'sent' && (
                        <>
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() =>
                              updateMutation.mutate({ id: match.id, data: { status: 'accepted' } })
                            }
                            title="Mark as accepted"
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              updateMutation.mutate({ id: match.id, data: { status: 'rejected' } })
                            }
                            title="Mark as rejected"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          if (confirm('Delete this match?')) {
                            deleteMutation.mutate(match.id)
                          }
                        }}
                        title="Delete match"
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
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
