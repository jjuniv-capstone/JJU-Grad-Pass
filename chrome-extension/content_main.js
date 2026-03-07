/**
 * MAIN world content script - 페이지 컨텍스트에서 실행
 * XHR 후킹으로 로그인 감지 → 로그인 응답에서 학적정보 + JSESSIONID 추출
 * → window.postMessage로 ISOLATED world에 전달
 */

(function () {
  // #jj_sync 해시가 없으면 아무것도 하지 않음
  if (!window.location.hash.includes("jj_sync")) return;
  console.log("[전주대 확장] 연동 모드 활성화");

  let sent = false;

  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function (method, url) {
    this._jj_url = url;
    this._jj_method = method;
    return origOpen.apply(this, arguments);
  };

  XMLHttpRequest.prototype.send = function (body) {
    this.addEventListener("load", function () {
      if (
        this._jj_url &&
        this._jj_url.includes("XMain") &&
        this._jj_method === "POST" &&
        this.responseText &&
        this.responseText.includes("JSESSIONID")
      ) {
        console.log("[전주대 확장] 로그인 성공 감지!");
        handleLoginResponse(this.responseText);
      }
    });
    return origSend.apply(this, arguments);
  };

  function handleLoginResponse(responseText) {
    if (sent) return;
    sent = true;

    try {
      // JSESSIONID 추출
      const jsessionMatch = responseText.match(/JSESSIONID[^>]*>([^<]+)</);
      const jsessionId = jsessionMatch ? jsessionMatch[1] : "";

      // 로그인 응답에서 학적정보 추출
      let member = parseRows(responseText, "ds_info");
      if (!member.length || !member[0].MEM_ID) {
        member = parseRows(responseText, "gds_member");
      }
      if (!member.length || !member[0].MEM_ID) {
        console.log("[전주대 확장] 학적정보 못 찾음");
        sent = false;
        return;
      }

      console.log("[전주대 확장] 학번:", member[0].MEM_ID, "JSESSIONID:", jsessionId ? "있음" : "없음");

      // 학적정보 + JSESSIONID를 서버로 전달 (졸업정보는 서버가 조회)
      window.postMessage(
        {
          type: "JJ_SAVE_RESULT",
          data: { member: member[0], jsessionid: jsessionId },
        },
        "*"
      );
    } catch (err) {
      console.error("[전주대 확장] 에러:", err);
      sent = false;
    }
  }

  function parseRows(xml, datasetId) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, "text/xml");
    const datasets = doc.querySelectorAll("Dataset");
    for (const ds of datasets) {
      if (ds.getAttribute("id") === datasetId) {
        const rows = [];
        for (const row of ds.querySelectorAll("Row")) {
          const data = {};
          for (const col of row.querySelectorAll("Col")) {
            data[col.getAttribute("id")] = col.textContent || "";
          }
          if (Object.keys(data).length) rows.push(data);
        }
        return rows;
      }
    }
    return [];
  }
})();
