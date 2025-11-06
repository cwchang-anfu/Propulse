/**
 * PropulseIQ TypeScript Type Definitions
 */

// 使用者相關類型
export interface User {
  id: number;
  email: string;
  full_name?: string;
  subscription_tier: 'free' | 'pro' | 'business' | 'enterprise';
  created_at: string;
  last_login?: string;
}

export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// 新聞文章相關類型
export interface Article {
  id: number;
  title_short: string;
  source: string;
  url: string;
  published_at: string;
  category?: string;
  sentiment_score?: number;
  sentiment_label?: string;
  sentiment_color?: string;
  keywords?: string[];
}

export interface ArticleListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Article[];
}

// 情緒分析相關類型
export interface SentimentCurrent {
  current_score: number;
  current_label: string;
  current_color: string;
  article_count: number;
  period: string;
  last_updated: string;
}

export interface SentimentTrend {
  date: string;
  avg_sentiment: number;
  article_count: number;
  optimistic_count: number;
  pessimistic_count: number;
  neutral_count: number;
}

export interface SentimentTrendList {
  trends: SentimentTrend[];
  start_date: string;
  end_date: string;
}

// 月度報告相關類型
export interface MonthlyReport {
  id: number;
  year: number;
  month: number;
  avg_sentiment?: number;
  article_count?: number;
  optimistic_count?: number;
  pessimistic_count?: number;
  neutral_count?: number;
  trend_direction?: string;
  key_topics?: Record<string, any>;
  generated_at: string;
}

export interface MonthlyReportList {
  total: number;
  reports: MonthlyReport[];
}

// API 錯誤類型
export interface APIError {
  detail: string;
}
