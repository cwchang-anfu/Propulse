/**
 * Dashboard Page
 * 主儀表板頁面
 */
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import type { SentimentCurrent, Article } from '@/types';
import { TrendingDown, TrendingUp, Minus } from 'lucide-react';

export default function Dashboard() {
  const [current, setCurrent] = useState<SentimentCurrent | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [sentimentData, articlesData] = await Promise.all([
        apiClient.getCurrentSentiment(),
        apiClient.getArticles({ page: 1, page_size: 10, sort_by: 'latest' }),
      ]);

      setCurrent(sentimentData);
      setArticles(articlesData.items);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">載入中...</div>;
  }

  const getSentimentIcon = (score?: number) => {
    if (!score) return <Minus className="w-5 h-5" />;
    if (score > 0.2) return <TrendingUp className="w-5 h-5" />;
    if (score < -0.2) return <TrendingDown className="w-5 h-5" />;
    return <Minus className="w-5 h-5" />;
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">市場情緒總覽</h1>

      {/* 當前情緒指標 */}
      {current && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">當前市場情緒</h2>
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div
                className="text-6xl font-bold mb-2"
                style={{ color: current.current_color }}
              >
                {current.current_score.toFixed(2)}
              </div>
              <div className="text-xl text-gray-600 mb-2">
                {current.current_label}
              </div>
              <div className="text-sm text-gray-500">
                {current.period} · 基於 {current.article_count} 篇新聞
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 最新新聞分析 */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">最新新聞分析</h2>
        <div className="space-y-3">
          {articles.map((article) => (
            <div
              key={article.id}
              className="flex items-start justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span
                    className="sentiment-badge"
                    style={{
                      backgroundColor: article.sentiment_color,
                      color: 'white',
                    }}
                  >
                    {getSentimentIcon(article.sentiment_score)}
                    <span className="ml-1">
                      {article.sentiment_score?.toFixed(2) || 'N/A'}
                    </span>
                  </span>
                  <span className="text-sm text-gray-500">{article.source}</span>
                </div>
                <h3 className="text-sm font-medium text-gray-900">
                  {article.title_short}
                </h3>
                {article.keywords && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {article.keywords.slice(0, 5).map((keyword, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-4 text-sm text-blue-600 hover:text-blue-800 whitespace-nowrap"
              >
                查看完整報導 →
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
