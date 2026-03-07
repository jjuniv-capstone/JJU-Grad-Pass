/**
 * ISOLATED world content script
 * content_main.js(MAIN world)에서 postMessage로 받은 결과를
 * chrome.runtime.sendMessage로 background에 전달
 */

window.addEventListener("message", (event) => {
  if (event.data && event.data.type === "JJ_SAVE_RESULT") {
    console.log("[전주대 확장] 결과 수신, background로 전달...");
    chrome.runtime.sendMessage({
      type: "SAVE_RESULT",
      data: event.data.data,
    });
  }
});
