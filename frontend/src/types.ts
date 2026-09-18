export type SubscriberStatus =
  | "active"
  | "inactive";

export type CampaignStatus =
  | "draft"
  | "scheduled"
  | "sending"
  | "sent"
  | "failed";

export interface User {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Subscriber {
  id: number;
  name: string;
  email: string;
  status: SubscriberStatus;
  created_at: string;
  updated_at: string;
}

export interface SubscriberListResponse {
  items: Subscriber[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface Campaign {
  id: number;
  title: string;
  subject: string;
  preview_text: string | null;
  content: string;
  cta_text: string | null;
  cta_url: string | null;
  audience_description: string | null;
  status: CampaignStatus;
  scheduled_at: string | null;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignInput {
  title: string;
  subject: string;
  preview_text?: string;
  content: string;
  cta_text?: string;
  cta_url?: string;
  audience_description?: string;
}

export interface Analytics {
  campaign_id: number;
  total_recipients: number;
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  bounced: number;
  complained: number;
  unsubscribed: number;
  failed: number;
  delivery_rate: number;
  open_rate: number;
  click_rate: number;
  bounce_rate: number;
  complaint_rate: number;
  unsubscribe_rate: number;
}

export interface AIGeneration {
  subject: string;
  preview_text: string;
  content: string;
  cta_text: string;
}

export interface AIAnalysis {
  summary: string;
  strengths: string[];
  issues: string[];
  recommendations: string[];
}

export interface CampaignSendResponse {
  message: string;
  campaign_id: number;
  task_id: string;
  status: CampaignStatus;
}