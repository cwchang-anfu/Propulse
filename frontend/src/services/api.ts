/**
 * API Client
 * 與後端 API 溝通的客戶端
 */
import axios, { AxiosInstance } from 'axios';
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  ArticleListResponse,
  Article,
  SentimentCurrent,
  SentimentTrendList,
  MonthlyReport,
  MonthlyReportList,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 請求攔截器：添加 JWT Token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 回應攔截器：處理錯誤
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token 過期，清除並重新導向登入
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== 認證相關 API ==========

  async register(data: RegisterRequest): Promise<User> {
    const response = await this.client.post('/api/v1/auth/register', data);
    return response.data;
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await this.client.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // 儲存 Token
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  logout() {
    localStorage.removeItem('access_token');
  }

  // ========== 新聞文章相關 API ==========

  async getArticles(params: {
    page?: number;
    page_size?: number;
    source?: string;
    sentiment_type?: string;
    sort_by?: string;
  }): Promise<ArticleListResponse> {
    const response = await this.client.get('/api/v1/articles/', { params });
    return response.data;
  }

  async getArticle(id: number): Promise<Article> {
    const response = await this.client.get(`/api/v1/articles/${id}`);
    return response.data;
  }

  // ========== 情緒分析相關 API ==========

  async getCurrentSentiment(): Promise<SentimentCurrent> {
    const response = await this.client.get('/api/v1/sentiment/current');
    return response.data;
  }

  async getSentimentTrend(months: number = 6): Promise<SentimentTrendList> {
    const response = await this.client.get('/api/v1/sentiment/trend', {
      params: { months },
    });
    return response.data;
  }

  async getMonthlySentiment(year: number, month: number) {
    const response = await this.client.get(`/api/v1/sentiment/monthly/${year}/${month}`);
    return response.data;
  }

  // ========== 報告相關 API ==========

  async getMonthlyReports(): Promise<MonthlyReportList> {
    const response = await this.client.get('/api/v1/reports/monthly');
    return response.data;
  }

  async getMonthlyReport(year: number, month: number): Promise<MonthlyReport> {
    const response = await this.client.get(`/api/v1/reports/monthly/${year}/${month}`);
    return response.data;
  }

  async exportReport(year: number, month: number, format: string) {
    const response = await this.client.get(
      `/api/v1/reports/export/${year}/${month}/${format}`,
      {
        responseType: format === 'pdf' ? 'blob' : 'json',
      }
    );
    return response.data;
  }
}

// 導出單例
export const apiClient = new APIClient();
