# 將開發分支合併到 main 的步驟

## ⚠️ 重要說明
Claude Code 不能直接推送到 main/master 分支（安全限制）
以下步驟需要**您手動執行**

## 📝 本地合併步驟

```bash
# 1. 確保在 Propulse 目錄下
cd /path/to/Propulse

# 2. 確認當前分支的所有變更都已推送
git status

# 3. 創建或切換到 main 分支
git checkout -b main  # 如果 main 不存在
# 或
git checkout main     # 如果已存在

# 4. 合併開發分支
git merge claude/propulseiq-real-estate-sentiment-saas-011CUrPb7w7TN1zWLgoisR9w

# 5. 檢查合併結果
git log --oneline -10

# 6. 推送到遠端 main（如果您有權限）
git push origin main
```

## 🌐 使用 Pull Request（推薦）

### GitHub 方式：

1. 訪問倉庫頁面：`https://github.com/cwchang-anfu/Propulse`

2. 點擊「Pull requests」→「New pull request」

3. 設定：
   ```
   base: main (或 master)
   compare: claude/propulseiq-real-estate-sentiment-saas-011CUrPb7w7TN1zWLgoisR9w
   ```

4. 填寫 PR 標題與說明：
   ```
   Title: feat: Implement PropulseIQ Real Estate Sentiment Analysis Platform
   
   Description:
   完整實作 PropulseIQ 房市脈動智析系統
   
   ## 主要功能
   - AI 情感分析（Claude API）
   - 多層級訂閱系統
   - 批次處理架構
   - 完整前後端實作
   
   ## 技術棧
   - 後端：FastAPI + PostgreSQL + Redis + Celery
   - 前端：React + TypeScript + TailwindCSS
   - 部署：Docker Compose
   
   詳細說明請見 README.md
   ```

5. 點擊「Create pull request」

6. Review 後點擊「Merge pull request」

### GitLab/Bitbucket 方式：

類似流程，在對應平台建立 Merge Request

## 📊 合併前檢查清單

- [ ] 所有功能都已測試
- [ ] README.md 文檔完整
- [ ] .env.example 已更新
- [ ] 沒有包含敏感資訊
- [ ] Docker Compose 可以正常啟動
- [ ] 測試數據腳本可以執行

## 🎯 合併後的分支結構

```
main (或 master)
├── 包含完整的 PropulseIQ 系統
├── 61 個檔案，4,354+ 行代碼
└── 可以直接使用的生產代碼

claude/propulseiq-*
└── 開發分支（可以保留或刪除）
```

## 💡 為什麼不能直接推送到 main？

這是 Claude Code 的安全機制：
- 防止 AI 意外覆蓋主分支
- 強制使用 Pull Request 流程
- 確保有人工 Review 的機會
- 保護生產代碼的穩定性

## 🔄 後續開發流程

如果需要繼續開發新功能：

```bash
# 1. 從 main 創建新的功能分支
git checkout main
git pull origin main
git checkout -b feature/new-feature

# 2. 開發並提交
git add .
git commit -m "feat: Add new feature"

# 3. 推送並創建 PR
git push origin feature/new-feature
# 然後在 GitHub 上創建 Pull Request
```

---

**總結**：開發分支（`claude/*`）已經包含完整代碼，您只需要通過 PR 合併到 main 即可！
