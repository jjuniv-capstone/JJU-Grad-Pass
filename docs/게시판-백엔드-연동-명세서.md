# 게시판 백엔드 연동 명세서

> 프론트엔드 구현 기준 | DB/API 연동 시 참고용  
> 릴레이션 스키마(게시판, 게시글, 댓글) 기준 정렬  
> 작성일: 2026-02

---

## 1. 개요

게시판은 **강의평가**와 **커뮤니티(익명/복학생/부전공/복수전공)** 두 종류로 구분됩니다.

| 구분 | 설명 | URL |
|------|------|-----|
| 강의평가 | 과목별 교수 평가, 평점, 상세후기 | `/board/course`, `/board/detail/<id>` |
| 커뮤니티 | 익명/복학생/부전공/복수전공 카테고리별 글 | `/board/community?cat=<category>`, `/board/community/detail/<id>` |

---

## 2. URL 라우팅 (현재 구조)

| URL | 화면 | 비고 |
|-----|------|------|
| `/board` | 강의평가 목록 | |
| `/board/course` | 강의평가 목록 | |
| `/board/community` | 커뮤니티 목록 | `?cat=anonymous|returning|minor|double` |
| `/board/detail/<post_id>` | 강의평가 상세 | |
| `/board/community/detail/<post_id>` | 커뮤니티 상세 | |
| `/board/write/course` | 강의평가 글쓰기 | |
| `/board/write/community` | 커뮤니티 글쓰기 | |

---

## 3. 데이터 구조

### 3.1 강의평가 (Course Evaluation)

#### 목록 카드
```json
{
  "id": 1,
  "subject": "데이터베이스",
  "professor": "김교수",
  "rating": 4
}
```

#### 상세
```json
{
  "id": 1,
  "subject": "데이터베이스",
  "professor": "김교수",
  "semester": "4학년 1학기",
  "rating": 4,
  "workload": "없음",
  "team_project": "있음",
  "attendance": "직접호명",
  "content": "과제가 많긴 하지만 실무에 도움되는...",
  "comment_count": 2,
  "comments": [
    { "author": "익명", "text": "저도 수강했는데 공감해요!" },
    { "author": "익명", "text": "팀플 조원 잘 만나시길 바랍니다." }
  ]
}
```

#### 글쓰기 폼 필드 (name 속성)
| name | 타입 | 설명 | 값/옵션 |
|------|------|------|---------|
| professor | string | 교수명 | |
| subject | string | 과목명 | |
| rating | string | 평점 | 1~5 |
| workload | string | 과제량 | none, very_low, low, medium, high, very_high |
| team_project | string | 팀프로젝트 여부 | no, yes |
| attendance | string | 출석방식 | direct, electronic, none |
| content | string | 상세 후기 | |

**workload 값 매핑**
- none: 없음
- very_low: 매우 적음
- low: 적음
- medium: 보통
- high: 많음
- very_high: 매우 많음

**attendance 값 매핑**
- direct: 직접 호명
- electronic: 전자 출석
- none: 출석 체크 안함

---

### 3.2 커뮤니티 (익명/복학생/부전공/복수전공)

#### 목록 카드
```json
{
  "id": 1,
  "title": "졸업요건 확인하는 거 아시는 분",
  "preview": "학교 포털 어디에서 확인하는지 모르겠어요 ㅠㅠ",
  "comment_count": 12
}
```

#### 상세
```json
{
  "id": 1,
  "title": "졸업요건 확인하는 거 아시는 분",
  "content": "학교 포털 어디에서 확인하는지 모르겠어요 ㅠㅠ\n\n졸업요건 체크하는 메뉴가...",
  "comment_count": 2,
  "comments": [
    { "author": "익명", "text": "학생지원팀에 문의해보세요!" }
  ]
}
```

#### 글쓰기 폼 필드 (name 속성)
| name | 타입 | 설명 | 값/옵션 |
|------|------|------|---------|
| category | string | 카테고리 | anonymous, returning, minor, double |
| title | string | 제목 | |
| content | string | 내용 | |

#### category 값 매핑
- anonymous: 익명
- returning: 복학생
- minor: 부전공
- double: 복수전공

---

### 3.3 댓글 (공통)

```json
{
  "author": "익명",
  "text": "댓글 내용"
}
```

- 강의평가/커뮤니티 모두 동일 구조
- 익명 게시판은 author를 "익명"으로 고정

---

## 4. API 엔드포인트 제안

### 4.1 강의평가

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/board/course` | 목록 조회 (검색: professor, subject) |
| GET | `/api/board/course/<id>` | 상세 조회 |
| POST | `/api/board/course` | 글 작성 |
| POST | `/api/board/course/<id>/comments` | 댓글 작성 |

### 4.2 커뮤니티

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/board/community` | 목록 조회 (query: cat, search) |
| GET | `/api/board/community/<id>` | 상세 조회 |
| POST | `/api/board/community` | 글 작성 |
| POST | `/api/board/community/<id>/comments` | 댓글 작성 |

### 4.3 검색 파라미터

**강의평가 목록**
- `professor`: 교수명
- `subject`: 과목명 또는 과목코드

**커뮤니티 목록**
- `cat`: anonymous | returning | minor | double
- `search`: 과목명 또는 과목코드 (선택)

---

## 5. DB 테이블 (릴레이션 스키마 기준)

### 5.1 게시판

| 컬럼 | 타입 | 설명 |
|------|------|------|
| 게시판ID | PK | |
| 게시판명 | VARCHAR | 강의평가, 익명, 복학생, 부전공, 복수전공 |

**초기 데이터 예시**
| 게시판ID | 게시판명 |
|----------|----------|
| 1 | 강의평가 |
| 2 | 익명 |
| 3 | 복학생 |
| 4 | 부전공 |
| 5 | 복수전공 |

---

### 5.2 게시글

| 컬럼 | 타입 | 설명 |
|------|------|------|
| 게시글ID | PK | |
| 제목 | VARCHAR | 제목 (강의평가: 과목명, 커뮤니티: 글 제목) |
| 생성일 | DATETIME | |
| 내용 | TEXT | 본문 |
| 게시판ID | FK | 게시판(게시판ID) 참조 |
| 학번 | FK | 사용자(학번) 참조 |

**강의평가 전용 확장 컬럼** (게시판ID=1일 때 사용, NULL 허용)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| 교수명 | VARCHAR | |
| 과목명 | VARCHAR | (제목과 동일 값 가능) |
| 수강학기 | VARCHAR | 예: 4학년 1학기 |
| 평점 | INT | 1~5 |
| 과제량 | VARCHAR | none, very_low, low, medium, high, very_high |
| 팀프로젝트여부 | VARCHAR | no, yes |
| 출석방식 | VARCHAR | direct, electronic, none |

---

### 5.3 댓글

| 컬럼 | 타입 | 설명 |
|------|------|------|
| 댓글ID | PK | |
| 내용 | TEXT | 댓글 본문 |
| 작성일 | DATETIME | |
| 게시글ID | FK | 게시글(게시글ID) 참조 |
| 학번 | FK | 사용자(학번) 참조 |

**익명 게시판**: 학번은 DB에 저장하되, API 응답 시 `author`는 "익명"으로 마스킹

---

### 5.4 관계 요약

| 관계 | 연결 |
|------|------|
| 등록하다 | 게시글.게시판ID → 게시판.게시판ID |
| 게시판작성하다 | 게시글.학번 → 사용자.학번 |
| 댓글달다 | 댓글.게시글ID → 게시글.게시글ID |
| 댓글작성하다 | 댓글.학번 → 사용자.학번 |

**comment_count**: `SELECT COUNT(*) FROM 댓글 WHERE 게시글ID = ?`

---

### 5.5 게시판ID ↔ 프론트엔드 매핑

| 게시판ID | 게시판명 | URL / cat |
|----------|----------|-----------|
| 1 | 강의평가 | /board/course |
| 2 | 익명 | cat=anonymous |
| 3 | 복학생 | cat=returning |
| 4 | 부전공 | cat=minor |
| 5 | 복수전공 | cat=double |

---

## 6. 프론트엔드 연동 포인트

### 6.1 현재 동작 (mock)
- 글쓰기 폼 제출 → `e.preventDefault()`, console.log, alert
- 댓글 등록 → `e.preventDefault()`, console.log, alert
- 목록/상세 → Flask에서 mock 데이터로 템플릿 렌더링

### 6.2 연동 시 변경 필요
1. **글쓰기**: form `action` 설정 또는 JS에서 `fetch('/api/board/course', { method: 'POST', body: formData })` 호출
2. **댓글 등록**: `fetch('/api/board/course/<id>/comments', { method: 'POST', ... })` 호출
3. **목록/상세**: Flask 라우트에서 DB 조회 후 템플릿에 전달 (또는 SPA 전환 시 fetch로 API 호출)

### 6.3 프론트엔드 ↔ DB 필드 매핑

| 프론트엔드 필드 | DB (게시글/댓글) |
|-----------------|------------------|
| id | 게시글ID |
| title | 제목 |
| subject | 과목명 (강의평가) 또는 제목 |
| content | 내용 |
| professor | 교수명 (강의평가) |
| rating | 평점 |
| comment_count | COUNT(댓글) |
| comments[].author | 학번 → "익명" 마스킹 (커뮤니티) |
| comments[].text | 댓글.내용 |

---

## 7. 참고 파일

| 파일 | 용도 |
|------|------|
| `backend/app/routes/board.py` | 현재 라우트, mock 데이터 구조 |
| `frontend/templates/board/*.html` | 템플릿, form name 속성 |
| `frontend/static/js/api.js` | API 호출 유틸 (fetchApi) |

---

## 8. 체크리스트 (백엔드 연동 시)

- [ ] DB 테이블 생성 (게시판, 게시글, 댓글) - 릴레이션 스키마 기준
- [ ] 게시글 테이블에 강의평가 확장 컬럼 추가 (교수명, 과목명, 평점 등)
- [ ] 강의평가 목록 API (게시판ID=1, 검색 지원)
- [ ] 강의평가 상세 API
- [ ] 강의평가 글쓰기 API
- [ ] 강의평가 댓글 API
- [ ] 커뮤니티 목록 API (게시판ID=2~5, cat 파라미터)
- [ ] 커뮤니티 상세 API
- [ ] 커뮤니티 글쓰기 API
- [ ] 커뮤니티 댓글 API
- [ ] comment_count 조회 (댓글 테이블 COUNT)
- [ ] Flask 라우트에서 DB 조회로 전환
