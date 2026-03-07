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
          // 인스타 로그아웃 후 알림 표시
          chrome.scripting.executeScript({
            target: { tabId: sender.tab.id },
            func: () => {
              alert("학적정보를 성공적으로 가져왔습니다!\n홈으로 돌아가서 조회 결과를 확인하세요.");
              window.location.href = "http://localhost:5000/";
            },
          });
        }
      })
      .catch((err) => {
        console.error("[전주대 확장] 서버 전송 에러:", err);
        if (sender.tab) {
          chrome.scripting.executeScript({
            target: { tabId: sender.tab.id },
            func: () => {
              alert("학적정보 전송에 실패했습니다. 다시 시도해주세요.");
            },
          });
        }
      });
  }
});

console.log("[전주대 확장] 백그라운드 시작됨");
