# JJU-Grad-Pass

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=black)
![Chrome Extension](https://img.shields.io/badge/Chrome_Extension-Manifest_V3-4285F4?logo=googlechrome&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> 전주대학교 졸업 요건 진단 시스템 — 캡스톤 프로젝트

---

## 소개

전주대학교 인스타(inSTAR) 시스템과 연동하여 **학적정보, 졸업이수기준, 학기별 성적, 개설강좌**를 자동으로 조회하고 졸업 요건 충족 여부를 진단하는 웹 서비스입니다.

**학생의 비밀번호는 우리 서버를 거치지 않습니다.** Chrome 확장 프로그램이 인스타 공식 페이지의 로그인 응답만 감지하여 학적정보를 가져옵니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **학적정보 연동** | Chrome 확장으로 인스타 로그인 감지 후 학적정보 자동 수집 |
| **졸업이수기준 조회** | 졸업 총괄 및 이수항목별 충족/미충족 현황 확인 |
| **학기별 성적 조회** | 입학년도~현재까지 전 학기 성적 (드롭다운 UI) |
| **개설강좌 조회** | 현재 학기 개설강좌를 이수구분별로 확인 (드롭다운 UI) |
| **게시판** | 자유게시판, 과목별 게시판 |

---

## 연동 흐름

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 우리 사이트 │───▶│ 인스타 페이지  │───▶│ Chrome 확장   │───▶│ Flask 백엔드  │
│ 연동 버튼   │    │ 학생 직접 로그인│    │ 로그인 응답 감지│    │ 졸업/성적 조회 │
└──────────┘    └──────────────┘    │ 학적정보 추출  │    │ 결과 페이지 표시│
                                    └──────────────┘    └──────────────┘
```

---

## 프로젝트 구조

```
capstone/
├── backend/                        # Flask 백엔드
│   ├── app/
│   │   ├── __init__.py             # 앱 초기화
│   │   ├── config.py               # 설정
│   │   ├── routes/
│   │   │   ├── api.py              # 공통 API
│   │   │   ├── board.py            # 게시판 라우트
│   │   │   └── instar.py           # 인스타 연동 API
│   │   ├── services/
│   │   │   └── instar_service.py   # 인스타 스크래핑 로직
│   │   ├── models/
│   │   └── utils/
│   ├── requirements.txt
│   └── run.py
│
├── frontend/                       # 프론트엔드
│   ├── templates/
│   │   ├── layout.html             # 공통 레이아웃
│   │   ├── index.html              # 메인 페이지
│   │   ├── result.html             # 학적정보 조회 결과
│   │   └── board/                  # 게시판 템플릿
│   └── static/
│       ├── css/                    # 스타일시트
│       └── js/                     # 클라이언트 스크립트
│
├── chrome-extension/               # Chrome 확장 프로그램
│   ├── manifest.json               # 확장 프로그램 설정 (Manifest V3)
│   ├── background.js               # 서비스 워커
│   ├── content.js                  # ISOLATED world 스크립트
│   └── content_main.js             # MAIN world 스크립트 (XHR 후킹)
│
└── docs/                           # 프로젝트 문서
```

---

## 실행 방법

### 1단계: 백엔드 서버 실행

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python run.py
```

http://localhost:5000 접속

### 2단계: Chrome 확장 프로그램 설치

1. Chrome에서 `chrome://extensions` 접속
2. 우측 상단 **개발자 모드** 활성화
3. **압축해제된 확장 프로그램을 로드합니다** 클릭
4. `chrome-extension/` 폴더 선택

### 3단계: 학적정보 연동 테스트

1. http://localhost:5000 에서 **학적정보 연동** 버튼 클릭
2. 인스타 로그인 페이지가 열리면 전주대 학번/비밀번호로 로그인
3. 로그인 성공 시 자동으로 결과 페이지(`/result`)로 이동
4. 학적정보, 졸업이수기준, 성적, 개설강좌 확인

---

## API

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| `POST` | `/api/instar/save-result` | Chrome 확장에서 학적정보 저장 |
| `GET` | `/api/instar/result` | 저장된 학적정보 조회 |

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **백엔드** | Python, Flask |
| **프론트엔드** | HTML, CSS, JavaScript, Jinja2 |
| **확장 프로그램** | Chrome Manifest V3, XHR Hooking |
| **연동 대상** | 전주대학교 inSTAR (nexacro 플랫폼) |

---

## 라이선스

MIT License
