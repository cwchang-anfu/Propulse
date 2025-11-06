"""
Seed Data Script
建立測試數據
"""
import sys
from datetime import datetime, timedelta
from random import choice, uniform, randint
from app.database import SessionLocal, engine
from app.models import Base, User, Article, SentimentScore
from app.utils.security import get_password_hash

# 測試新聞標題和內容
SAMPLE_NEWS = [
    {
        "title": "央行升息半碼 房市買氣轉淡觀望氣氛濃",
        "content": "中央銀行宣布升息半碼，房地產市場買氣明顯轉淡，購屋者多持觀望態度。業者表示，部分建案銷售速度明顯放緩，市場進入盤整期。",
        "sentiment": -0.35
    },
    {
        "title": "新建案熱銷 北市蛋白區買家回流",
        "content": "台北市外圍蛋白區新建案熱銷，買家逐漸回流。建商表示，合理價格帶的產品受到首購族青睞，市場需求穩定。",
        "sentiment": 0.28
    },
    {
        "title": "房貸利率創十年新高 購屋成本增加",
        "content": "房貸利率攀升至十年新高，購屋族每月還款壓力增加。專家建議，現階段購屋應審慎評估自身財務狀況。",
        "sentiment": -0.42
    },
    {
        "title": "政府推動社會住宅 釋出萬戶名額",
        "content": "政府積極推動社會住宅政策，今年將釋出上萬戶名額。此舉有助減輕年輕人租屋負擔，獲得各界正面評價。",
        "sentiment": 0.15
    },
    {
        "title": "房價居高不下 民眾購屋意願低迷",
        "content": "最新調查顯示，高房價持續壓抑民眾購屋意願。超過七成受訪者表示，現階段房價過高，短期內不考慮購屋。",
        "sentiment": -0.48
    },
    {
        "title": "建商推案量創新高 市場供給充足",
        "content": "今年建商推案量創歷史新高，市場供給充足。分析師認為，充裕的供給將有助於穩定房價，對購屋族是利多。",
        "sentiment": 0.22
    },
    {
        "title": "都更案順利推動 老舊社區煥然一新",
        "content": "多個都更案順利推動，老舊社區將煥然一新。居民對未來居住環境改善充滿期待，周邊房價也獲得支撐。",
        "sentiment": 0.32
    },
    {
        "title": "打炒房條例上路 投資客退場",
        "content": "打炒房條例正式上路，投資客紛紛退場。房仲業者觀察，市場投資性買盤明顯減少，交易回歸自住需求。",
        "sentiment": -0.18
    },
    {
        "title": "捷運新線通車 沿線房價看漲",
        "content": "捷運新線即將通車，沿線房價看漲。不動產業者表示，交通便利性提升，吸引自住買盤進駐，區域發展前景看好。",
        "sentiment": 0.38
    },
    {
        "title": "房市成交量萎縮 業者憂心年底旺季不旺",
        "content": "今年房市成交量明顯萎縮，業者憂心年底傳統旺季可能不旺。多數建案採取價換量策略，希望衝刺買氣。",
        "sentiment": -0.28
    }
]

SOURCES = ["工商時報", "經濟日報", "聯合新聞網", "自由時報", "中時新聞網"]
CATEGORIES = ["貨幣政策", "市場分析", "政府政策", "建案推案", "都市更新"]


def create_test_data():
    """建立測試數據"""
    db = SessionLocal()

    try:
        print("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)

        print("👤 Creating test users...")

        # 建立測試使用者
        users_data = [
            {
                "email": "free@example.com",
                "password": "password123",
                "full_name": "Free User",
                "tier": "free"
            },
            {
                "email": "pro@example.com",
                "password": "password123",
                "full_name": "Pro User",
                "tier": "pro"
            },
            {
                "email": "business@example.com",
                "password": "password123",
                "full_name": "Business User",
                "tier": "business"
            }
        ]

        for user_data in users_data:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    subscription_tier=user_data["tier"]
                )
                db.add(user)
                print(f"  ✓ Created user: {user_data['email']} (password: {user_data['password']})")

        db.commit()

        print("📰 Creating test articles...")

        # 建立測試文章
        base_date = datetime.now()

        for i in range(100):
            # 從樣本中選擇或生成隨機標題
            if i < len(SAMPLE_NEWS):
                news = SAMPLE_NEWS[i]
                title = news["title"]
                content = news["content"]
            else:
                news = choice(SAMPLE_NEWS)
                title = f"{news['title']} (測試 {i+1})"
                content = news["content"]

            # 隨機日期（最近 90 天）
            days_ago = randint(0, 90)
            published_at = base_date - timedelta(days=days_ago)

            article = Article(
                title=title,
                source=choice(SOURCES),
                url=f"https://example.com/news/{i+1}",
                published_at=published_at,
                category=choice(CATEGORIES),
                raw_content=content
            )

            db.add(article)
            db.flush()  # 獲取 article.id

            # 建立對應的情緒分數
            if i < len(SAMPLE_NEWS):
                sentiment_score = SAMPLE_NEWS[i]["sentiment"]
            else:
                sentiment_score = uniform(-0.8, 0.8)

            sentiment = SentimentScore(
                article_id=article.id,
                sentiment_score=sentiment_score,
                confidence=uniform(0.7, 0.95),
                keywords=["房價", "買氣", "市場", "政策", "投資"][:randint(3, 5)],
                analysis_reason="測試數據自動生成",
                model_version="test-model"
            )

            db.add(sentiment)

            if (i + 1) % 10 == 0:
                print(f"  ✓ Created {i + 1} articles...")

        db.commit()

        print("\n✅ Seed data created successfully!")
        print("\n📋 Test Users:")
        print("  - free@example.com / password123 (Free Tier)")
        print("  - pro@example.com / password123 (Pro Tier)")
        print("  - business@example.com / password123 (Business Tier)")
        print(f"\n📰 Created 100 test articles with sentiment scores")

    except Exception as e:
        print(f"\n❌ Error creating seed data: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
