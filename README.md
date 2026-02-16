# JJU-Grad-Pass

전주대학교 졸업 요건 관리 시스템 캡스톤 프로젝트

## About

전주대학교 졸업 요건 관리 시스템 캡스톤 프로젝트

Flask + HTML/CSS/JS 기반으로 개발되었습니다.

---

## 프로젝트 구조

```
capstone/
├── backend/           # Flask 백엔드
│   ├── app/
│   │   ├── __init__.py    # 앱 초기화
│   │   ├── config.py      # 설정
│   │   ├── routes/        # 라우트 (URL 매핑)
│   │   ├── models/        # DB 모델
│   │   ├── services/      # 비즈니스 로직
│   │   └── utils/         # 유틸리티
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
│
├── frontend/          # HTML, CSS, JS 프론트엔드
│   ├── templates/     # Jinja2 HTML 템플릿
│   │   ├── components/  # 재사용 템플릿 조각
│   │   ├── layout.html
│   │   └── index.html
│   ├── static/        # 정적 파일 (브라우저에서 직접 로드)
│   │   ├── css/       # 스타일시트
│   │   ├── js/        # JavaScript
│   │   ├── images/    # 이미지 (png, jpg, svg 등)
│   │   └── fonts/     # 웹폰트
│   └── pages/         # 페이지별 추가 리소스 (필요 시)
│
└── docs/              # 프로젝트 문서
```

---

## 백엔드 폴더 구조 (역할별 분리)

백엔드는 **레이어드 아키텍처**로 관심사를 분리했습니다.

| 폴더 | 역할 | 설명 |
|------|------|------|
| **routes/** | 라우트 계층 | URL과 요청을 받아서 처리 흐름 결정 |
| **models/** | 모델 계층 | DB 테이블과 매핑되는 데이터 구조 |
| **services/** | 서비스 계층 | 비즈니스 로직 처리 |
| **utils/** | 유틸리티 | 여러 곳에서 쓰는 공통 함수 |

**요청 흐름**: `routes` → `services` → `models` → DB

---

## 프론트엔드 폴더 구조

| 폴더 | 역할 | 설명 |
|------|------|------|
| **templates/** | HTML 템플릿 | Jinja2로 렌더링되는 페이지 마크업 |
| **templates/components/** | 템플릿 조각 | 헤더, 푸터 등 재사용 HTML 파트 |
| **static/** | 정적 파일 | 서버 처리 없이 브라우저가 직접 로드하는 파일 |
| **static/css/** | 스타일시트 | 레이아웃, 색상, 반응형 등 스타일 정의 |
| **static/js/** | JavaScript | 클릭, API 호출, DOM 조작 등 클라이언트 로직 |
| **static/images/** | 이미지 | 아이콘, 배경, 로고 등 (png, jpg, svg 등) |
| **static/fonts/** | 웹폰트 | 커스텀 폰트 파일 (woff, woff2 등) |
| **pages/** | 페이지 리소스 | 페이지별로 분리된 추가 에셋 (필요 시 사용) |

---

## 실행 방법

1. 가상환경 생성 및 활성화
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

2. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

3. 서버 실행
   ```bash
   python run.py
   ```

4. 브라우저에서 http://localhost:5000 접속

---

## License

MIT License
