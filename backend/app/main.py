"""
PropulseIQ - FastAPI Main Application
房市脈動智析系統 - 後端主程式
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, articles, sentiment, reports

# 建立 FastAPI 應用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="台灣房地產新聞情緒分析 SaaS 平台",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路徑
@app.get("/")
def root():
    """根路徑"""
    return {
        "message": "Welcome to PropulseIQ API",
        "description": "台灣房地產新聞情緒分析系統",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# 健康檢查
@app.get("/health")
def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}


# 註冊路由
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    articles.router,
    prefix=f"{settings.API_V1_PREFIX}/articles",
    tags=["Articles"]
)

app.include_router(
    sentiment.router,
    prefix=f"{settings.API_V1_PREFIX}/sentiment",
    tags=["Sentiment Analysis"]
)

app.include_router(
    reports.router,
    prefix=f"{settings.API_V1_PREFIX}/reports",
    tags=["Reports"]
)


# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    print("🚀 PropulseIQ API is starting...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 Debug Mode: {settings.DEBUG}")


# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時執行"""
    print("👋 PropulseIQ API is shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
