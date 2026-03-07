# 백엔드 구현 요청서

## 현재 상태

프론트엔드 페이지는 만들어져 있으나, 백엔드 로직(DB, 인증)이 없는 상태입니다.

### 완성된 페이지
| URL | 파일 | 설명 | 상태 |
|-----|------|------|------|
| `/` | `home_overview_before.html` | 로그인 전 소개 페이지 | UI만 완료 |
| `/home` | `home_overview_after.html` | 로그인 후 홈 | UI만 완료 |
| `/login` | `login/login.html` | 로그인 | UI만 완료 (백엔드 없음) |
| `/signup` | `login/signup.html` | 회원가입 | UI만 완료 (백엔드 없음) |
| `/result` | `result.html` | 학적정보 조회 결과 | 인스타 연동 완료 |
| `/recommend` | `recommend/recommend.html` | 과목 추천 | 인스타 데이터 기반 완료 |
| `/board` | `board/` | 게시판 | mock 데이터 기반 |

---

## 1. 회원가입 API

### 엔드포인트
`POST /api/auth/signup`

### 요청 (JSON)
```json
{
  "name": "홍길동",
  "student_id": "202168043",
  "password": "비밀번호",
  "password_confirm": "비밀번호",
  "major_type": "single"
}
```

### 회원가입 폼 필드 (signup.html 기준)
| 필드 | 타입 | 설명 |
|------|------|------|
| 이름 | text | 필수 |
| 학번 | text | 9자리 숫자, 필수, 중복 불가 |
| 비밀번호 | password | 필수 |
| 비밀번호 확인 | password | 비밀번호와 일치 확인 |
| 전공 형태 | select | single(단일전공), double(복수전공), minor(부전공) |

### 응답
```json
// 성공
{ "success": true, "message": "회원가입 완료" }

// 실패
{ "success": false, "message": "이미 등록된 학번입니다." }
```

### 유효성 검증
- 학번: 9자리 숫자, 중복 체크
- 비밀번호: 최소 8자 이상
- 비밀번호 확인: 일치 여부
- 비밀번호 저장: 반드시 해싱 (bcrypt 등)

---

## 2. 로그인 API

### 엔드포인트
`POST /api/auth/login`

### 요청 (JSON)
```json
{
  "student_id": "202168043",
  "password": "비밀번호"
}
```

### 로그인 폼 필드 (login.html 기준)
| 필드 | 타입 | 설명 |
|------|------|------|
| 학번 | text | 필수 |
| 비밀번호 | password | 필수 |

### 응답
```json
// 성공
{ "success": true, "message": "로그인 성공", "user": { "name": "홍길동", "student_id": "202168043" } }

// 실패
{ "success": false, "message": "학번 또는 비밀번호가 올바르지 않습니다." }
```

### 세션/인증 방식
- Flask session 또는 JWT 중 택 1
- 로그인 성공 시 `/home`으로 리다이렉트
- 로그인 안 한 상태에서 `/home`, `/result`, `/recommend` 접근 시 `/login`으로 리다이렉트

---

## 3. 로그아웃 API

### 엔드포인트
`POST /api/auth/logout`

### 응답
```json
{ "success": true, "message": "로그아웃 완료" }
```

로그아웃 후 `/`(소개 페이지)로 리다이렉트

---

## 4. DB 스키마

프론트엔드 릴레이션 스키마 기준으로 구현해주세요.

### 1단계: 우선 구현 (회원가입/로그인에 필요)

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

### 2단계: 이후 확장 (전체 스키마)

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

### 추천 DB: SQLite
- 파일 위치: `backend/instance/app.db`
- ORM: Flask-SQLAlchemy
- **1단계(users, department)만 먼저 구현하고, 나머지는 기능 개발 시 추가**

---

## 5. 필요한 패키지

```
Flask-SQLAlchemy
Flask-Bcrypt (또는 werkzeug.security)
```

`requirements.txt`에 추가 필요

---

## 6. 파일 구조 가이드

```
backend/app/
├── routes/
│   └── auth.py          # 회원가입, 로그인, 로그아웃 API
├── models/
│   └── user.py          # User 모델 (이미 파일 존재)
├── services/
│   └── auth_service.py  # 인증 비즈니스 로직
```

`__init__.py`에 블루프린트 등록:
```python
from app.routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
```

---

## 7. 페이지 접근 제어

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

## 8. 프론트엔드 연동 참고

로그인 페이지(`login.html`)에서 JS로 API 호출하는 예시:

```javascript
document.querySelector('.login-btn').addEventListener('click', async () => {
    const student_id = document.getElementById('student-id').value;
    const password = document.getElementById('password').value;

    const resp = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id, password })
    });
    const result = await resp.json();

    if (result.success) {
        window.location.href = '/home';
    } else {
        alert(result.message);
    }
});
```

회원가입도 동일한 패턴으로 `/api/auth/signup` 호출

---

## 우선순위

1. DB 설정 (SQLite + SQLAlchemy)
2. User 모델
3. 회원가입 API
4. 로그인/로그아웃 API
5. 페이지 접근 제어 (로그인 체크)
