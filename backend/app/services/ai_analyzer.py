"""
AI Analyzer Service
使用 Claude API 進行情感分析
"""
import json
import logging
from typing import Dict, Optional
from anthropic import Anthropic
from app.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI 情感分析器"""

    def __init__(self):
        """初始化 Anthropic 客戶端"""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.AI_MODEL
        self.max_retries = settings.AI_MAX_RETRIES

    def _build_prompt(self, title: str, content: str) -> str:
        """
        建構分析 Prompt

        Args:
            title: 新聞標題
            content: 新聞內容

        Returns:
            完整的分析 Prompt
        """
        return f"""請分析以下台灣房地產新聞的市場情緒，並給出 -1 到 +1 的評分：

評分標準：
- -1.0 到 -0.5：極度悲觀（如：重大利空、市場崩盤、嚴厲打房）
- -0.5 到 -0.2：悲觀（如：打房政策、買氣下滑、房價下跌）
- -0.2 到 0.2：中性（如：數據報導、政策說明、市場觀察）
- 0.2 到 0.5：樂觀（如：交易回溫、利多消息、房價上漲）
- 0.5 到 1.0：極度樂觀（如：房價大漲、供不應求、投資熱潮）

新聞標題：{title}
新聞內容：{content}

請以 JSON 格式回覆（不要包含任何其他文字）：
{{
  "sentiment_score": -0.45,
  "confidence": 0.87,
  "keywords": ["升息", "買氣", "觀望", "房價", "政策"],
  "reason": "新聞報導央行升息導致購屋意願下降，多個建案銷售不如預期"
}}"""

    def analyze_sentiment(self, title: str, content: str) -> Optional[Dict]:
        """
        分析新聞情感

        Args:
            title: 新聞標題
            content: 新聞內容

        Returns:
            分析結果字典，包含：
            - sentiment_score: 情緒分數 (-1 到 1)
            - confidence: 信心度 (0 到 1)
            - keywords: 關鍵字列表
            - reason: 分析原因說明

        Raises:
            Exception: 當 API 調用失敗時
        """
        prompt = self._build_prompt(title, content)

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Analyzing sentiment (attempt {attempt + 1}/{self.max_retries})")

                # 調用 Claude API
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # 解析回應
                response_text = message.content[0].text.strip()

                # 嘗試從回應中提取 JSON
                # 有時 Claude 會在 JSON 外包裹其他文字
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    result = json.loads(json_text)
                else:
                    result = json.loads(response_text)

                # 驗證結果
                if not self._validate_result(result):
                    logger.warning(f"Invalid result format: {result}")
                    continue

                logger.info(f"Successfully analyzed sentiment: {result['sentiment_score']}")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                if attempt == self.max_retries - 1:
                    raise

            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")
                if attempt == self.max_retries - 1:
                    raise

        return None

    def _validate_result(self, result: Dict) -> bool:
        """
        驗證分析結果格式

        Args:
            result: 分析結果字典

        Returns:
            是否有效
        """
        required_fields = ['sentiment_score', 'confidence', 'keywords', 'reason']

        # 檢查必要欄位
        if not all(field in result for field in required_fields):
            return False

        # 檢查數值範圍
        if not (-1 <= result['sentiment_score'] <= 1):
            return False

        if not (0 <= result['confidence'] <= 1):
            return False

        # 檢查關鍵字是否為列表
        if not isinstance(result['keywords'], list):
            return False

        return True

    def batch_analyze(self, articles: list) -> list:
        """
        批次分析多篇新聞

        Args:
            articles: 新聞列表，每個元素為 (article_id, title, content)

        Returns:
            分析結果列表
        """
        results = []

        for article_id, title, content in articles:
            try:
                result = self.analyze_sentiment(title, content)
                if result:
                    results.append({
                        'article_id': article_id,
                        'sentiment_score': result['sentiment_score'],
                        'confidence': result['confidence'],
                        'keywords': result['keywords'],
                        'analysis_reason': result['reason'],
                        'model_version': self.model
                    })
            except Exception as e:
                logger.error(f"Failed to analyze article {article_id}: {e}")
                continue

        return results
