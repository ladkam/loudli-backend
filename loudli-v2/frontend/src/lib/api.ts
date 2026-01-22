import axios from 'axios'
import type {
  AuthTokens,
  User,
  Podcast,
  PodcastWithEpisodes,
  PodcastSearchResult,
  Episode,
  Category,
  Campaign,
  CampaignWithDetails,
  CampaignStats,
  Message,
  LoginFormData,
  RegisterFormData,
  PodcastFormData,
  CampaignFormData,
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post<AuthTokens>(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token } = response.data

          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch {
        // Refresh failed, clear tokens
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (data: LoginFormData): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>('/auth/login', data)
    return response.data
  },

  register: async (data: RegisterFormData): Promise<User> => {
    const response = await api.post<User>('/auth/register', {
      email: data.email,
      password: data.password,
      profile: {
        user_type: data.user_type,
        first_name: data.first_name,
        last_name: data.last_name,
        company_name: data.company_name,
      },
    })
    return response.data
  },

  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}

// Users API
export const usersApi = {
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  updateMe: async (data: Partial<User>): Promise<User> => {
    const response = await api.patch<User>('/users/me', data)
    return response.data
  },

  updateProfile: async (data: Partial<User['profile']>): Promise<User['profile']> => {
    const response = await api.patch<User['profile']>('/users/me/profile', data)
    return response.data
  },
}

// Podcasts API
export const podcastsApi = {
  list: async (params?: {
    skip?: number
    limit?: number
    category_id?: number
    search?: string
  }): Promise<Podcast[]> => {
    const response = await api.get<Podcast[]>('/podcasts', { params })
    return response.data
  },

  getMyPodcasts: async (): Promise<Podcast[]> => {
    const response = await api.get<Podcast[]>('/podcasts/my')
    return response.data
  },

  get: async (id: number): Promise<PodcastWithEpisodes> => {
    const response = await api.get<PodcastWithEpisodes>(`/podcasts/${id}`)
    return response.data
  },

  create: async (data: PodcastFormData): Promise<Podcast> => {
    const response = await api.post<Podcast>('/podcasts', data)
    return response.data
  },

  update: async (id: number, data: Partial<PodcastFormData>): Promise<Podcast> => {
    const response = await api.patch<Podcast>(`/podcasts/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/podcasts/${id}`)
  },

  sync: async (id: number): Promise<Podcast> => {
    const response = await api.post<Podcast>(`/podcasts/${id}/sync`)
    return response.data
  },

  searchExternal: async (query: string, maxResults?: number): Promise<PodcastSearchResult[]> => {
    const response = await api.get<PodcastSearchResult[]>('/podcasts/search/external', {
      params: { query, max_results: maxResults },
    })
    return response.data
  },

  getTrending: async (maxResults?: number, language?: string): Promise<PodcastSearchResult[]> => {
    const response = await api.get<PodcastSearchResult[]>('/podcasts/trending', {
      params: { max_results: maxResults, language },
    })
    return response.data
  },

  import: async (data: { podcast_index_id?: number; rss_feed_url?: string }): Promise<Podcast> => {
    const response = await api.post<Podcast>('/podcasts/import', data)
    return response.data
  },

  // Episodes
  getEpisodes: async (
    podcastId: number,
    params?: { skip?: number; limit?: number }
  ): Promise<Episode[]> => {
    const response = await api.get<Episode[]>(`/podcasts/${podcastId}/episodes`, { params })
    return response.data
  },

  createEpisode: async (
    podcastId: number,
    data: Partial<Episode>
  ): Promise<Episode> => {
    const response = await api.post<Episode>(`/podcasts/${podcastId}/episodes`, data)
    return response.data
  },

  // Categories
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get<Category[]>('/podcasts/categories/all')
    return response.data
  },
}

// Campaigns API
export const campaignsApi = {
  list: async (params?: {
    skip?: number
    limit?: number
    status_filter?: string
  }): Promise<Campaign[]> => {
    const response = await api.get<Campaign[]>('/campaigns', { params })
    return response.data
  },

  get: async (id: number): Promise<CampaignWithDetails> => {
    const response = await api.get<CampaignWithDetails>(`/campaigns/${id}`)
    return response.data
  },

  create: async (data: CampaignFormData): Promise<Campaign> => {
    const response = await api.post<Campaign>('/campaigns', data)
    return response.data
  },

  update: async (id: number, data: Partial<Campaign>): Promise<Campaign> => {
    const response = await api.patch<Campaign>(`/campaigns/${id}`, data)
    return response.data
  },

  getStats: async (): Promise<CampaignStats> => {
    const response = await api.get<CampaignStats>('/campaigns/stats')
    return response.data
  },

  // Messages
  getMessages: async (
    campaignId: number,
    params?: { skip?: number; limit?: number }
  ): Promise<Message[]> => {
    const response = await api.get<Message[]>(`/campaigns/${campaignId}/messages`, { params })
    return response.data
  },

  sendMessage: async (
    campaignId: number,
    data: { content: string; message_type?: string; offer_amount?: number }
  ): Promise<Message> => {
    const response = await api.post<Message>(`/campaigns/${campaignId}/messages`, data)
    return response.data
  },

  markMessagesRead: async (campaignId: number): Promise<{ marked_read: number }> => {
    const response = await api.post<{ marked_read: number }>(
      `/campaigns/${campaignId}/messages/read`
    )
    return response.data
  },
}

export default api
