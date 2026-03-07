# 백엔드 구현 명세서

> 프론트엔드 릴레이션 스키마 기준 | 백엔드 구현 시 참고용

---

## 1. 현재 상태

프론트엔드 페이지는 만들어져 있으나, 백엔드 로직(DB, 인증)이 없는 상태입니다.

| URL | 파일 | 설명 | 상태 |
|-----|------|------|------|
| `/` | `home_overview_before.html` | 로그인 전 소개 페이지 | UI 완료 |
| `/home` | `home_overview_after.html` | 로그인 후 홈 | UI 완료 |
| `/login` | `login/login.html` | 로그인 | UI + API 호출 JS 완료 |
| `/signup` | `login/signup.html` | 회원가입 | UI + API 호출 JS 완료 |
| `/result` | `result.html` | 학적정보 조회 결과 | 인스타 연동 완료 |
| `/recommend` | `recommend/recommend.html` | 과목 추천 | 인스타 데이터 기반 완료 |
| `/board` | `board/` | 게시판 | mock 데이터 기반 |

---

## 2. 릴레이션 스키마

### 2.1 엔티티 (테이블)

```
학과 (학과코드(PK), 학과명, 단과대명)
사용자 (학번(PK), 비밀번호, 이름, 이수학기수, 총이수학점, 학과코드(FK), 전공형태)
개설과목 (과목코드(PK), 과목명, 기본이수구분, 정원, 개설학기, 학점, 담당교수, 분반, 성적방식)
수강내역 (수강내역ID(PK), 수강상태, 인정학점, 취득성적, 학번(FK), 과목코드(FK))
졸업요건 (요건ID(PK), 단위, 항목명, 이수영역구분, 기준, 학과코드(FK), 설정년도)
졸업판정결과 (판정ID(PK), 판정일, 판정결과, 부족요약, 학번(FK))
게시판 (게시판ID(PK), 게시판명)
게시글 (게시글ID(PK), 제목, 생성일, 내용, 게시판ID(FK), 학번(FK))
댓글 (댓글ID(PK), 내용, 작성일, 게시글ID(FK), 학번(FK))
신청하다 (학번(FK), 과목코드(FK))
기준되다 (요건ID(FK), 판정ID(FK))
```

> **참고**: 사용자 테이블의 `전공형태`는 릴레이션 스키마 원본에는 없었으나,
> 회원가입 시 단일전공/복수전공/부전공을 구분해야 하므로 추가함.
> 스키마 문서 업데이트 시 반영 필요.

### 2.2 관계

| 관계 | 연결 (FK) | 비고 |
|------|-----------|------|
| 소속되다 | 사용자.학과코드 → 학과.학과코드 | 사용자가 학과에 소속 |
| 수강하다 | 수강내역.학번 → 사용자.학번 | 수강 이력 |
| 참조하다 | 수강내역.과목코드 → 개설과목.과목코드 | 과목 정보 참조 |
| 신청하다 | 학번(FK), 과목코드(FK) | 수강신청 (다대다) |
| 설정하다 | 졸업요건.학과코드 → 학과.학과코드 | 학과별 졸업요건 설정 |
| 기준되다 | 요건ID(FK), 판정ID(FK) | 졸업요건-판정 연결 (다대다) |
| 판정받다 | 졸업판정결과.학번 → 사용자.학번 | 졸업 판정 |
| 등록하다 | 게시글.게시판ID → 게시판.게시판ID | 게시글이 게시판에 등록 |
| 게시판작성하다 | 게시글.학번 → 사용자.학번 | 사용자가 글 작성 |
| 댓글달다 | 댓글.게시글ID → 게시글.게시글ID | 게시글에 댓글 |
| 댓글작성하다 | 댓글.학번 → 사용자.학번 | 사용자가 댓글 작성 |

---

## 3. DB 스키마 (SQL)

### 3.1 1단계: 우선 구현 (회원가입/로그인)

```sql
-- 학과
CREATE TABLE department (
    dept_code VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    college_name VARCHAR(100)
);

-- 사용자
CREATE TABLE users (
    student_id VARCHAR(9) PRIMARY KEY,
    password_hash VARCHAR(256) NOT NULL,
    name VARCHAR(60) NOT NULL,
    semester_count INTEGER DEFAULT 0,
    total_credits INTEGER DEFAULT 0,
    dept_code VARCHAR(10),
    major_type VARCHAR(10) DEFAULT 'single',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_code) REFERENCES department(dept_code)
);
```

> `semester_count`, `total_credits`, `dept_code`는 회원가입 시 입력받지 않음.
> 인스타(학적정보 시스템) 연동 시 자동으로 채워지는 값.
> `major_type`은 회원가입 폼에서 입력받음 (single/double/minor).

### 3.2 2단계: 전체 스키마

```sql
-- 개설과목
CREATE TABLE course (
    course_code VARCHAR(20) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    category VARCHAR(20),
    capacity INTEGER,
    semester VARCHAR(10),
    credits INTEGER,
    professor VARCHAR(60),
    section VARCHAR(5),
    grade_method VARCHAR(10)
);

-- 수강내역
CREATE TABLE enrollment (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR(10),
    approved_credits INTEGER,
    grade VARCHAR(5),
    student_id VARCHAR(9),
    course_code VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES users(student_id),
    FOREIGN KEY (course_code) REFERENCES course(course_code)
);

-- 졸업요건
CREATE TABLE graduation_req (
    req_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit VARCHAR(20),
    item_name VARCHAR(100),
    category VARCHAR(20),
    standard VARCHAR(20),
    dept_code VARCHAR(10),
    req_year INTEGER,
    FOREIGN KEY (dept_code) REFERENCES department(dept_code)
);

-- 졸업판정결과
CREATE TABLE graduation_result (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_date DATE,
    result VARCHAR(10),
    deficiency_summary TEXT,
    student_id VARCHAR(9),
    FOREIGN KEY (student_id) REFERENCES users(student_id)
);

-- 게시판
CREATE TABLE board (
    board_id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_name VARCHAR(50) NOT NULL
);

-- 게시글
CREATE TABLE post (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    content TEXT,
    board_id INTEGER,
    student_id VARCHAR(9),
    FOREIGN KEY (board_id) REFERENCES board(board_id),
    FOREIGN KEY (student_id) REFERENCES users(student_id)
);

-- 댓글
CREATE TABLE comment (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    post_id INTEGER,
    student_id VARCHAR(9),
    FOREIGN KEY (post_id) REFERENCES post(post_id),
    FOREIGN KEY (student_id) REFERENCES users(student_id)
);

-- 수강신청 (다대다)
CREATE TABLE course_apply (
    student_id VARCHAR(9),
    course_code VARCHAR(20),
    PRIMARY KEY (student_id, course_code),
    FOREIGN KEY (student_id) REFERENCES users(student_id),
    FOREIGN KEY (course_code) REFERENCES course(course_code)
);

-- 졸업요건-판정 연결 (다대다)
CREATE TABLE req_result_link (
    req_id INTEGER,
    result_id INTEGER,
    PRIMARY KEY (req_id, result_id),
    FOREIGN KEY (req_id) REFERENCES graduation_req(req_id),
    FOREIGN KEY (result_id) REFERENCES graduation_result(result_id)
);
```

### 3.3 DB 설정

- DB: SQLite
- 파일 위치: `backend/instance/app.db`
- ORM: Flask-SQLAlchemy

`config.py`에 추가 필요:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'backend' / 'instance' / 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

`__init__.py`에서 `db.init_app(app)` 호출 및 테이블 생성 로직 추가 필요.

---

## 4. 인증 API

### 4.1 회원가입

**엔드포인트:** `POST /api/auth/signup`

**요청:**
```json
{
  "name": "홍길동",
  "student_id": "202168043",
  "password": "비밀번호",
  "password_confirm": "비밀번호",
  "major_type": "single"
}
```

**폼 필드 (signup.html 기준):**
| 필드 | id | 타입 | 설명 |
|------|----|------|------|
| 이름 | name | text | 필수 |
| 학번 | student-id | text | 9자리 숫자, 필수, 중복 불가 |
| 비밀번호 | password | password | 필수, 8자 이상 |
| 비밀번호 확인 | password-confirm | password | 비밀번호와 일치 확인 |
| 전공 형태 | major-type | select | single/double/minor |

**응답:**
```json
// 성공
{ "success": true, "message": "회원가입 완료" }

// 실패
{ "success": false, "message": "이미 등록된 학번입니다." }
```

**유효성 검증:**
- 학번: 9자리 숫자, 중복 체크
- 비밀번호: 최소 8자 이상
- 비밀번호 확인: 일치 여부
- 비밀번호 저장: 반드시 해싱 (bcrypt 등)

> 프론트엔드에서도 동일한 유효성 검사를 수행하지만, 백엔드에서도 반드시 검증해야 함.

### 4.2 로그인

**엔드포인트:** `POST /api/auth/login`

**요청:**
```json
{
  "student_id": "202168043",
  "password": "비밀번호"
}
```

**폼 필드 (login.html 기준):**
| 필드 | id | 타입 |
|------|----|------|
| 학번 | student-id | text |
| 비밀번호 | password | password |

**응답:**
```json
// 성공
{ "success": true, "message": "로그인 성공", "user": { "name": "홍길동", "student_id": "202168043" } }

// 실패
{ "success": false, "message": "학번 또는 비밀번호가 올바르지 않습니다." }
```

**세션/인증 방식:**
- Flask session 또는 JWT 중 택 1
- 로그인 성공 시 프론트에서 `/home`으로 이동

### 4.3 로그아웃

**엔드포인트:** `POST /api/auth/logout`

**응답:**
```json
{ "success": true, "message": "로그아웃 완료" }
```

로그아웃 후 프론트에서 `/`(소개 페이지)로 이동.

---

## 5. 페이지 접근 제어

| 페이지 | 로그인 필요 |
|--------|------------|
| `/` (소개) | X |
| `/login` | X |
| `/signup` | X |
| `/home` | O |
| `/result` | O |
| `/recommend` | O |
| `/board` | O |

로그인 필요한 페이지에 비로그인 접근 시 → `/login`으로 리다이렉트

---

## 6. 게시판 API

### 6.1 URL 라우팅 (현재 프론트엔드 구조)

| URL | 화면 |
|-----|------|
| `/board` `/board/course` | 강의평가 목록 |
| `/board/community` | 커뮤니티 목록 (`?cat=anonymous\|returning\|minor\|double`) |
| `/board/detail/<id>` | 강의평가 상세 |
| `/board/community/detail/<id>` | 커뮤니티 상세 |
| `/board/write/course` | 강의평가 글쓰기 |
| `/board/write/community` | 커뮤니티 글쓰기 |

### 6.2 API 엔드포인트

**강의평가:**
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/board/course` | 목록 (검색: professor, subject) |
| GET | `/api/board/course/<id>` | 상세 |
| POST | `/api/board/course` | 글 작성 |
| POST | `/api/board/course/<id>/comments` | 댓글 작성 |

**커뮤니티:**
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/board/community` | 목록 (query: cat, search) |
| GET | `/api/board/community/<id>` | 상세 |
| POST | `/api/board/community` | 글 작성 |
| POST | `/api/board/community/<id>/comments` | 댓글 작성 |

### 6.3 게시판 초기 데이터

| 게시판ID | 게시판명 | URL / cat |
|----------|----------|-----------|
| 1 | 강의평가 | /board/course |
| 2 | 익명 | cat=anonymous |
| 3 | 복학생 | cat=returning |
| 4 | 부전공 | cat=minor |
| 5 | 복수전공 | cat=double |

### 6.4 강의평가 데이터 구조

**목록:**
```json
{
  "id": 1,
  "board_id": 1,
  "student_id": null,
  "created_at": "2026-01-10",
  "subject": "데이터베이스",
  "professor": "김교수",
  "rating": 4
}
```

**상세:**
```json
{
  "id": 1,
  "board_id": 1,
  "student_id": null,
  "created_at": "2026-01-10",
  "subject": "데이터베이스",
  "professor": "김교수",
  "semester": "4학년 1학기",
  "rating": 4,
  "workload": "없음",
  "team_project": "있음",
  "attendance": "직접호명",
  "content": "과제가 많긴 하지만...",
  "comment_count": 2,
  "comments": [
    { "id": 1, "post_id": 1, "student_id": null, "author": "익명", "text": "내용", "created_at": "2026-01-11" }
  ]
}
```

**강의평가 확장 컬럼** (게시글 테이블에 추가, NULL 허용):

| 컬럼 | 타입 | 값 |
|------|------|-----|
| professor | VARCHAR | 교수명 |
| subject | VARCHAR | 과목명 |
| semester | VARCHAR | 수강학기 |
| rating | INT | 1~5 |
| workload | VARCHAR | none/very_low/low/medium/high/very_high |
| team_project | VARCHAR | no/yes |
| attendance | VARCHAR | direct/electronic/none |

### 6.5 커뮤니티 데이터 구조

**목록:**
```json
{
  "id": 1,
  "board_id": 2,
  "student_id": null,
  "created_at": "2026-01-05",
  "title": "졸업요건 확인하는 거 아시는 분",
  "preview": "학교 포털 어디에서...",
  "comment_count": 12
}
```

**상세:**
```json
{
  "id": 1,
  "board_id": 2,
  "student_id": null,
  "created_at": "2026-01-05",
  "title": "졸업요건 확인하는 거 아시는 분",
  "content": "학교 포털 어디에서...",
  "comment_count": 2,
  "comments": [
    { "id": 1, "post_id": 1, "student_id": null, "author": "익명", "text": "내용", "created_at": "2026-01-05" }
  ]
}
```

### 6.6 댓글 구조 (공통)

```json
{
  "id": 1,
  "post_id": 1,
  "student_id": null,
  "author": "익명",
  "text": "댓글 내용",
  "created_at": "2026-01-05"
}
```

- `student_id`: DB에는 학번 저장, API 응답 시 `null` 처리 (익명)
- `author`: 항상 `"익명"`으로 응답

### 6.7 글쓰기 폼 필드

**강의평가 (board_write_course.html):**
| name | 타입 | 필수 |
|------|------|------|
| professor | text | O |
| subject | text | O |
| rating | select (1~5) | O |
| workload | select | X |
| team_project | select | X |
| attendance | select | X |
| content | textarea | O |

**커뮤니티 (board_write_community.html):**
| name | 타입 | 필수 |
|------|------|------|
| category | select (anonymous/returning/minor/double) | O |
| title | text | O |
| content | textarea | O |

### 6.8 프론트엔드 연동 포인트

현재 글쓰기 폼은 `alert('API 연동 전')` 상태.
DB 연동 시 해당 부분을 실제 `fetch` 호출로 교체하면 됨.

---

## 7. 파일 구조 가이드

```
backend/app/
├── __init__.py         # Flask 앱 팩토리, 블루프린트 등록
├── config.py           # DB 설정 추가 필요
├── routes/
│   ├── __init__.py     # auth_bp 추가 등록 필요
│   ├── auth.py         # [신규] 회원가입, 로그인, 로그아웃 API
│   ├── board.py        # 게시판 (현재 mock → DB 연동 전환)
│   ├── api.py
│   └── instar.py
├── models/
│   └── user.py         # [수정] User 모델 구현 필요 (현재 주석만 있음)
├── services/
│   └── auth_service.py # [신규] 인증 비즈니스 로직
```

`__init__.py` 블루프린트 등록 추가:
```python
from app.routes import api_bp, board_bp, instar_bp, auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
```

---

## 8. 필요 패키지

```
Flask-SQLAlchemy
Flask-Bcrypt
```

`requirements.txt`에 추가 필요.

---

## 9. 구현 우선순위

1. DB 설정 (SQLite + SQLAlchemy + config.py)
2. User 모델 (`models/user.py`)
3. 회원가입 API (`POST /api/auth/signup`)
4. 로그인/로그아웃 API
5. 페이지 접근 제어 (로그인 체크 데코레이터)
6. 게시판 DB 연동 (mock → 실제 DB)

---

## 10. 체크리스트

**인증:**
- [ ] config.py에 SQLALCHEMY 설정 추가
- [ ] User 모델 구현 (models/user.py)
- [ ] auth.py 블루프린트 생성 및 등록
- [ ] 회원가입 API (학번 중복체크, 비밀번호 해싱)
- [ ] 로그인 API (세션 또는 JWT)
- [ ] 로그아웃 API
- [ ] 페이지 접근 제어 데코레이터

**게시판:**
- [ ] DB 테이블 생성 (게시판, 게시글, 댓글)
- [ ] 게시글 테이블에 강의평가 확장 컬럼 추가
- [ ] 강의평가 CRUD API
- [ ] 커뮤니티 CRUD API
- [ ] 댓글 API
- [ ] mock 데이터 → DB 조회로 전환
