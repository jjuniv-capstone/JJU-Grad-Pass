/**
 * content script에서 수집 결과를 받아 서버로 전송
 */

const SERVER_URL = "http://localhost:5000/api/instar/save-result";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SAVE_RESULT") {
    console.log("[전주대 확장] 데이터 수신, 서버로 전송...");

    fetch(SERVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.data),
    })
      .then((r) => r.json())
      .then((data) => {
        console.log("[전주대 확장] 서버 응답:", data);
        if (data.success && sender.tab) {
          chrome.tabs.update(sender.tab.id, {
            url: "http://localhost:5000/result",
          });
        }
      })
      .catch((err) => {
        console.error("[전주대 확장] 서버 전송 에러:", err);
      });
  }
});

console.log("[전주대 확장] 백그라운드 시작됨");
