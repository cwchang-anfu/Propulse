export default function Copyright() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">版權聲明</h1>
      <div className="card space-y-4">
        <section>
          <h2 className="text-xl font-semibold mb-2">資料來源說明</h2>
          <p className="text-gray-700">
            PropulseIQ 對公開發布的房地產相關新聞進行情緒分析，所有新聞內容的著作權歸原始媒體所有。
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-2">合理使用聲明</h2>
          <p className="text-gray-700">
            本平台僅提供新聞標題摘要（不超過20字）以及情緒分析結果，不對外提供完整新聞內容。
            所有新聞均提供原文連結，引導使用者至原始媒體網站閱讀完整內容。
          </p>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-2">侵權通知</h2>
          <p className="text-gray-700">
            如您認為本平台侵犯了您的著作權，請透過 legal@propulseiq.com 聯繫我們。
            我們將在收到通知後儘速處理。
          </p>
        </section>
      </div>
    </div>
  );
}
