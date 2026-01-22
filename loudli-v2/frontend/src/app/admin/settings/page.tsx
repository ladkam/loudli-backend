'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Settings, Plus, Save, Trash2, Eye, EyeOff, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { adminApi, SystemSetting } from '@/lib/api'

export default function AdminSettingsPage() {
  const queryClient = useQueryClient()
  const [editingKey, setEditingKey] = useState<string | null>(null)
  const [editValue, setEditValue] = useState('')
  const [showSecret, setShowSecret] = useState<Record<string, boolean>>({})
  const [newSetting, setNewSetting] = useState({
    key: '',
    value: '',
    description: '',
    is_secret: true,
  })
  const [showNewForm, setShowNewForm] = useState(false)

  const { data: settings, isLoading } = useQuery({
    queryKey: ['adminSettings'],
    queryFn: adminApi.getSettings,
  })

  const updateMutation = useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) =>
      adminApi.updateSetting(key, { value }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminSettings'] })
      setEditingKey(null)
      setEditValue('')
    },
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createSetting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminSettings'] })
      setShowNewForm(false)
      setNewSetting({ key: '', value: '', description: '', is_secret: true })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: adminApi.deleteSetting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminSettings'] })
    },
  })

  const handleSave = (key: string) => {
    updateMutation.mutate({ key, value: editValue })
  }

  const handleCreate = () => {
    if (newSetting.key) {
      createMutation.mutate(newSetting)
    }
  }

  const predefinedSettings = [
    {
      key: 'PODCAST_INDEX_API_KEY',
      description: 'Podcast Index API Key (get free at podcastindex.org)',
      is_secret: true,
    },
    {
      key: 'PODCAST_INDEX_API_SECRET',
      description: 'Podcast Index API Secret',
      is_secret: true,
    },
  ]

  // Check which predefined settings are missing
  const existingKeys = new Set(settings?.map((s) => s.key) || [])
  const missingSettings = predefinedSettings.filter((s) => !existingKeys.has(s.key))

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">API Settings</h1>
        <p className="text-gray-500 mt-1">Configure external API keys and system settings</p>
      </div>

      {/* Podcast Index Info */}
      <Card className="mb-6 border-primary-200 bg-primary-50">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Settings className="h-5 w-5 text-primary-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-primary-900">Podcast Index API</h3>
              <p className="text-sm text-primary-700 mt-1">
                To enable podcast search and trending features, you need API credentials from
                Podcast Index. They're free and take 2 minutes to get.
              </p>
              <a
                href="https://podcastindex.org/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center mt-2 text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                Get free API keys
                <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Missing Settings Alert */}
      {missingSettings.length > 0 && (
        <Card className="mb-6 border-yellow-200 bg-yellow-50">
          <CardContent className="p-4">
            <h3 className="font-medium text-yellow-900 mb-2">Missing Settings</h3>
            <p className="text-sm text-yellow-700 mb-3">
              The following settings need to be configured:
            </p>
            <div className="space-y-2">
              {missingSettings.map((setting) => (
                <button
                  key={setting.key}
                  onClick={() => {
                    setNewSetting({
                      ...setting,
                      value: '',
                    })
                    setShowNewForm(true)
                  }}
                  className="block w-full text-left p-2 bg-white rounded border border-yellow-200 hover:border-yellow-300 transition-colors"
                >
                  <div className="font-mono text-sm text-gray-900">{setting.key}</div>
                  <div className="text-xs text-gray-500">{setting.description}</div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Settings */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <h2 className="text-lg font-semibold">System Settings</h2>
          <Button size="sm" onClick={() => setShowNewForm(!showNewForm)}>
            <Plus className="h-4 w-4 mr-1" />
            Add Setting
          </Button>
        </CardHeader>
        <CardContent>
          {/* New Setting Form */}
          {showNewForm && (
            <div className="mb-6 p-4 border border-dashed border-gray-300 rounded-lg bg-gray-50">
              <h3 className="font-medium text-gray-900 mb-3">New Setting</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <Input
                  label="Key"
                  placeholder="SETTING_KEY"
                  value={newSetting.key}
                  onChange={(e) => setNewSetting({ ...newSetting, key: e.target.value })}
                />
                <Input
                  label="Value"
                  type={newSetting.is_secret ? 'password' : 'text'}
                  placeholder="Value"
                  value={newSetting.value}
                  onChange={(e) => setNewSetting({ ...newSetting, value: e.target.value })}
                />
              </div>
              <Input
                label="Description"
                placeholder="What this setting is for"
                value={newSetting.description}
                onChange={(e) => setNewSetting({ ...newSetting, description: e.target.value })}
                className="mb-4"
              />
              <div className="flex items-center gap-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newSetting.is_secret}
                    onChange={(e) => setNewSetting({ ...newSetting, is_secret: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-600">Secret (mask value)</span>
                </label>
                <div className="flex-1" />
                <Button variant="outline" onClick={() => setShowNewForm(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreate} isLoading={createMutation.isPending}>
                  Create
                </Button>
              </div>
            </div>
          )}

          {/* Settings List */}
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : settings?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No settings configured yet
            </div>
          ) : (
            <div className="space-y-4">
              {settings?.map((setting) => (
                <div
                  key={setting.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-mono text-sm font-medium text-gray-900">
                        {setting.key}
                      </div>
                      {setting.description && (
                        <div className="text-sm text-gray-500 mt-1">{setting.description}</div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {setting.is_secret && (
                        <button
                          onClick={() =>
                            setShowSecret((prev) => ({
                              ...prev,
                              [setting.key]: !prev[setting.key],
                            }))
                          }
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          {showSecret[setting.key] ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      )}
                      <button
                        onClick={() => {
                          if (confirm(`Delete setting "${setting.key}"?`)) {
                            deleteMutation.mutate(setting.key)
                          }
                        }}
                        className="p-1 text-red-400 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {editingKey === setting.key ? (
                    <div className="mt-3 flex items-center gap-2">
                      <Input
                        type={setting.is_secret && !showSecret[setting.key] ? 'password' : 'text'}
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        placeholder="Enter new value"
                        className="flex-1"
                      />
                      <Button
                        size="sm"
                        onClick={() => handleSave(setting.key)}
                        isLoading={updateMutation.isPending}
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingKey(null)
                          setEditValue('')
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <div className="mt-2 flex items-center gap-2">
                      <code className="flex-1 px-2 py-1 bg-gray-100 rounded text-sm">
                        {setting.is_secret && !showSecret[setting.key]
                          ? '••••••••'
                          : setting.value || '(not set)'}
                      </code>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingKey(setting.key)
                          setEditValue('')
                        }}
                      >
                        Edit
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
