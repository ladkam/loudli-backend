// User types
export type UserType = 'podcaster' | 'advertiser'

export interface UserProfile {
  id: number
  user_id: number
  user_type: UserType
  first_name: string | null
  last_name: string | null
  company_name: string | null
  bio: string | null
  profile_image_url: string | null
  phone: string | null
  website: string | null
  location: string | null
}

export interface User {
  id: number
  email: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  profile: UserProfile | null
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

// Podcast types
export interface Category {
  id: number
  name: string
  description: string | null
}

export interface Episode {
  id: number
  podcast_id: number
  title: string
  description: string | null
  audio_url: string
  episode_number: number | null
  season_number: number | null
  duration_seconds: number | null
  guid: string | null
  file_size_bytes: number | null
  published_at: string | null
  created_at: string
}

export interface Podcast {
  id: number
  owner_id: number
  title: string
  description: string | null
  cover_image_url: string | null
  website_url: string | null
  rss_feed_url: string | null
  podcast_index_id: number | null
  itunes_id: number | null
  total_episodes: number
  average_duration_seconds: number | null
  subscriber_count: number | null
  language: string | null
  author: string | null
  is_explicit: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  last_rss_sync: string | null
  categories: Category[]
}

export interface PodcastWithEpisodes extends Podcast {
  episodes: Episode[]
}

export interface PodcastSearchResult {
  id: number
  title: string
  description: string | null
  author: string | null
  image_url: string | null
  rss_feed_url: string | null
  website_url: string | null
  language: string | null
  categories: string[]
  episode_count: number | null
}

// Campaign types
export type CampaignStatus =
  | 'draft'
  | 'pending'
  | 'negotiating'
  | 'accepted'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'rejected'

export type MessageType = 'text' | 'audio' | 'file' | 'offer' | 'system'

export interface Message {
  id: number
  campaign_id: number
  sender_id: number
  content: string | null
  message_type: MessageType
  is_read: boolean
  offer_amount: number | null
  created_at: string
}

export interface Attachment {
  id: number
  campaign_id: number
  message_id: number | null
  filename: string
  file_url: string
  file_type: string | null
  file_size_bytes: number | null
  created_at: string
}

export interface Campaign {
  id: number
  advertiser_id: number
  podcast_id: number
  title: string
  description: string | null
  status: CampaignStatus
  budget: number | null
  price_per_episode: number | null
  currency: string
  start_date: string | null
  end_date: string | null
  episodes_count: number | null
  target_demographics: string | null
  impressions: number
  clicks: number
  created_at: string
  updated_at: string
}

export interface CampaignWithDetails extends Campaign {
  podcast_title: string | null
  advertiser_email: string | null
  messages: Message[]
  attachments: Attachment[]
  unread_count: number
}

export interface CampaignStats {
  total_campaigns: number
  active_campaigns: number
  total_budget: number
  total_impressions: number
  total_clicks: number
}

// Form types
export interface LoginFormData {
  email: string
  password: string
}

export interface RegisterFormData {
  email: string
  password: string
  user_type: UserType
  first_name?: string
  last_name?: string
  company_name?: string
}

export interface PodcastFormData {
  title: string
  description?: string
  website_url?: string
  rss_feed_url?: string
  language?: string
  author?: string
  is_explicit?: boolean
  category_ids?: number[]
}

export interface CampaignFormData {
  podcast_id: number
  title: string
  description?: string
  budget?: number
  price_per_episode?: number
  currency?: string
  start_date?: string
  end_date?: string
  episodes_count?: number
}
