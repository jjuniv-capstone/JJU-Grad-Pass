"""
게시판 페이지 라우트
- HTML 템플릿 렌더링만 수행 (API/DB 없음)
- 프론트엔드 페이지 서빙용
- 더미 데이터 구조는 docs/board-backend-api-spec.md 기준
"""
from flask import Blueprint, render_template, request

board_bp = Blueprint('board', __name__, url_prefix='/board')

# =====================================================================
# 강의평가 mock 데이터 (docs/board-backend-api-spec.md 3.1 기준)
# API 연동 시 이 데이터를 GET /api/board/course 응답으로 교체
# =====================================================================
COURSE_MOCK_POSTS = [
    # 게시글 스키마: 게시글ID(PK), 제목, 생성일, 내용, 게시판ID(FK)=1, 학번(FK)
    # 강의평가 확장: subject, professor, semester, rating, workload, team_project, attendance
    {'id': 1, 'subject': '데이터베이스', 'professor': '김교수', 'rating': 4,
     'board_id': 1, 'student_id': None, 'created_at': '2026-01-10'},
    {'id': 2, 'subject': '인공지능', 'professor': '이교수', 'rating': 3,
     'board_id': 1, 'student_id': None, 'created_at': '2026-01-15'},
    {'id': 3, 'subject': '운영체제', 'professor': '박교수', 'rating': 5,
     'board_id': 1, 'student_id': None, 'created_at': '2026-01-20'},
    {'id': 4, 'subject': '알고리즘', 'professor': '최교수', 'rating': 4,
     'board_id': 1, 'student_id': None, 'created_at': '2026-01-25'},
]

COURSE_MOCK_DETAIL = {
    1: {
        'id': 1,
        'board_id': 1,
        'student_id': None,       # DB에는 학번 저장, 응답 시 None(익명 처리)
        'created_at': '2026-01-10',
        'subject': '데이터베이스',
        'professor': '김교수',
        'semester': '4학년 1학기',
        'rating': 4,
        'workload': '없음',
        'team_project': '있음',
        'attendance': '직접호명',
        'content': '과제가 많긴 하지만 실무에 도움되는 내용들을 많이 배울 수 있습니다. 팀플이 있어서 조원 복불복이 좀 있어요. 중간고사, 기말고사 모두 서술형 위주입니다.',
        'comment_count': 2,
        'comments': [
            # 댓글 스키마: 댓글ID(PK), 내용, 작성일, 게시글ID(FK), 학번(FK)
            {'id': 1, 'post_id': 1, 'student_id': None, 'author': '익명', 'text': '저도 수강했는데 공감해요!', 'created_at': '2026-01-11'},
            {'id': 2, 'post_id': 1, 'student_id': None, 'author': '익명', 'text': '팀플 조원 잘 만나시길 바랍니다.', 'created_at': '2026-01-12'},
        ],
    },
    2: {
        'id': 2,
        'board_id': 1,
        'student_id': None,
        'created_at': '2026-01-15',
        'subject': '인공지능',
        'professor': '이교수',
        'semester': '3학년 2학기',
        'rating': 3,
        'workload': '보통',
        'team_project': '없음',
        'attendance': '전자출석',
        'content': '이론 위주 수업입니다. 중간·기말 모두 객관식이라 부담은 적어요. 다만 내용이 광범위해서 정리가 필요합니다.',
        'comment_count': 1,
        'comments': [
            {'id': 3, 'post_id': 2, 'student_id': None, 'author': '익명', 'text': '시험 범위가 넓어서 미리 준비하세요.', 'created_at': '2026-01-16'},
        ],
    },
    3: {
        'id': 3,
        'board_id': 1,
        'student_id': None,
        'created_at': '2026-01-20',
        'subject': '운영체제',
        'professor': '박교수',
        'semester': '3학년 1학기',
        'rating': 5,
        'workload': '많음',
        'team_project': '없음',
        'attendance': '직접호명',
        'content': '내용이 어렵지만 교수님 설명이 정말 명확합니다. 과제가 많아 힘들지만 실력이 많이 늘어요.',
        'comment_count': 0,
        'comments': [],
    },
    4: {
        'id': 4,
        'board_id': 1,
        'student_id': None,
        'created_at': '2026-01-25',
        'subject': '알고리즘',
        'professor': '최교수',
        'semester': '2학년 2학기',
        'rating': 4,
        'workload': '매우 많음',
        'team_project': '없음',
        'attendance': '출석체크 안함',
        'content': '과제량이 상당히 많지만 코딩 실력 향상에 큰 도움이 됩니다. 출석은 자유로워서 자기 관리가 중요합니다.',
        'comment_count': 1,
        'comments': [
            {'id': 4, 'post_id': 4, 'student_id': None, 'author': '익명', 'text': '과제 미루지 말고 꾸준히 하세요.', 'created_at': '2026-01-26'},
        ],
    },
}

# =====================================================================
# 커뮤니티 mock 데이터 (docs/board-backend-api-spec.md 3.2 기준)
# category 필드를 데이터 안에 포함 → 별도 ID 매핑 불필요
# API 연동 시 GET /api/board/community?cat=<category> 응답으로 교체
# =====================================================================
COMMUNITY_MOCK_POSTS = [
    # 게시글 스키마: 게시글ID(PK), 제목, 생성일, 내용, 게시판ID(FK), 학번(FK)
    # board_id: 2=익명, 3=복학생, 4=부전공, 5=복수전공
    {'id': 1, 'category': 'anonymous', 'board_id': 2, 'student_id': None, 'title': '졸업요건 확인하는 거 아시는 분', 'preview': '학교 포털 어디에서 확인하는지 모르겠어요 ㅠㅠ', 'comment_count': 12, 'created_at': '2026-01-05'},
    {'id': 2, 'category': 'anonymous', 'board_id': 2, 'student_id': None, 'title': '시험 기출 어디서 구해요?', 'preview': '중간고사 준비하는데 기출문제 구할 곳이 있을까요?', 'comment_count': 5, 'created_at': '2026-01-08'},
    {'id': 3, 'category': 'anonymous', 'board_id': 2, 'student_id': None, 'title': '과제 같이 하실 분 구해요', 'preview': '데이터베이스 과제 2번 같이 풀어보실 분 있나요?', 'comment_count': 3, 'created_at': '2026-01-12'},
    {'id': 4, 'category': 'returning', 'board_id': 3, 'student_id': None, 'title': '복학 후 수강신청 꿀팁', 'preview': '2년 만에 복학했는데 수강신청이 너무 달라졌어요. 후배님들 참고하세요.', 'comment_count': 8, 'created_at': '2026-01-06'},
    {'id': 5, 'category': 'returning', 'board_id': 3, 'student_id': None, 'title': '복학생 학점 인정 문의', 'preview': '군휴학 전에 들었던 과목 학점 인정 받으신 분 계신가요?', 'comment_count': 2, 'created_at': '2026-01-09'},
    {'id': 6, 'category': 'minor', 'board_id': 4, 'student_id': None, 'title': '부전공 심화과목 추천해주세요', 'preview': '경영 부전공 하는데 어떤 과목이 괜찮을까요?', 'comment_count': 7, 'created_at': '2026-01-07'},
    {'id': 7, 'category': 'minor', 'board_id': 4, 'student_id': None, 'title': '부전공 이수학점 문의', 'preview': '부전공 21학점 이수해야 하는데 18학점만 들었어요. 어떻게 해야 할까요?', 'comment_count': 4, 'created_at': '2026-01-11'},
    {'id': 8, 'category': 'double', 'board_id': 5, 'student_id': None, 'title': '복수전공 vs 부전공 차이', 'preview': '복수전공이랑 부전공이랑 뭐가 다른지 정리해주실 분 있나요?', 'comment_count': 15, 'created_at': '2026-01-03'},
    {'id': 9, 'category': 'double', 'board_id': 5, 'student_id': None, 'title': '복수전공 포기하고 부전공으로 전환', 'preview': '복수전공 부담이 커서 부전공으로 바꾸려고 하는데 절차가 어떻게 되나요?', 'comment_count': 6, 'created_at': '2026-01-14'},
]

COMMUNITY_MOCK_DETAIL = {
    # 게시글 스키마: 게시글ID(PK), 제목, 생성일, 내용, 게시판ID(FK), 학번(FK)
    # 댓글 스키마:  댓글ID(PK), 내용, 작성일, 게시글ID(FK), 학번(FK)
    1: {'id': 1, 'category': 'anonymous', 'board_id': 2, 'student_id': None, 'created_at': '2026-01-05',
        'title': '졸업요건 확인하는 거 아시는 분',
        'content': '학교 포털 어디에서 확인하는지 모르겠어요 ㅠㅠ\n\n졸업요건 체크하는 메뉴가 포털에 있는데 찾기가 어렵네요. 학과사무실에 문의해야 할까요?',
        'comment_count': 12,
        'comments': [
            {'id': 1, 'post_id': 1, 'student_id': None, 'author': '익명', 'text': '학생지원팀에 문의해보세요!', 'created_at': '2026-01-05'},
            {'id': 2, 'post_id': 1, 'student_id': None, 'author': '익명', 'text': '포털 로그인 > 학사 > 졸업요건 에 있던데요', 'created_at': '2026-01-06'},
        ]},
    2: {'id': 2, 'category': 'anonymous', 'board_id': 2, 'student_id': None, 'created_at': '2026-01-08',
        'title': '시험 기출 어디서 구해요?',
        'content': '중간고사 준비하는데 기출문제 구할 곳이 있을까요?\n\n선배님들 도움 부탁드려요.',
        'comment_count': 5,
        'comments': [
            {'id': 3, 'post_id': 2, 'student_id': None, 'author': '익명', 'text': '동아리나 스터디에서 공유하는 경우가 많아요', 'created_at': '2026-01-08'},
        ]},
    3: {'id': 3, 'category': 'anonymous', 'board_id': 2, 'student_id': None, 'created_at': '2026-01-12',
        'title': '과제 같이 하실 분 구해요',
        'content': '데이터베이스 과제 2번 같이 풀어보실 분 있나요?\n\n혼자 하기 어려워서요.',
        'comment_count': 3,
        'comments': []},
    4: {'id': 4, 'category': 'returning', 'board_id': 3, 'student_id': None, 'created_at': '2026-01-06',
        'title': '복학 후 수강신청 꿀팁',
        'content': '2년 만에 복학했는데 수강신청이 너무 달라졌어요. 후배님들 참고하세요.\n\n1. 미리 수강편람 확인\n2. 시간표 미리 짜두기\n3. 당일 새벽에 접속 추천',
        'comment_count': 8,
        'comments': [
            {'id': 4, 'post_id': 4, 'student_id': None, 'author': '익명', 'text': '감사합니다!', 'created_at': '2026-01-06'},
            {'id': 5, 'post_id': 4, 'student_id': None, 'author': '익명', 'text': '복학생 우선순위 있나요?', 'created_at': '2026-01-07'},
        ]},
    5: {'id': 5, 'category': 'returning', 'board_id': 3, 'student_id': None, 'created_at': '2026-01-09',
        'title': '복학생 학점 인정 문의',
        'content': '군휴학 전에 들었던 과목 학점 인정 받으신 분 계신가요?\n\n졸업요건에 포함되는지 확인하고 싶어요.',
        'comment_count': 2,
        'comments': []},
    6: {'id': 6, 'category': 'minor', 'board_id': 4, 'student_id': None, 'created_at': '2026-01-07',
        'title': '부전공 심화과목 추천해주세요',
        'content': '경영 부전공 하는데 어떤 과목이 괜찮을까요?\n\n전공이 컴공이라 경영은 처음이에요.',
        'comment_count': 7,
        'comments': [
            {'id': 6, 'post_id': 6, 'student_id': None, 'author': '익명', 'text': '마케팅원론 추천해요', 'created_at': '2026-01-07'},
        ]},
    7: {'id': 7, 'category': 'minor', 'board_id': 4, 'student_id': None, 'created_at': '2026-01-11',
        'title': '부전공 이수학점 문의',
        'content': '부전공 21학점 이수해야 하는데 18학점만 들었어요. 어떻게 해야 할까요?\n\n졸업 전에 3학점 더 들어야 하는데요.',
        'comment_count': 4,
        'comments': []},
    8: {'id': 8, 'category': 'double', 'board_id': 5, 'student_id': None, 'created_at': '2026-01-03',
        'title': '복수전공 vs 부전공 차이',
        'content': '복수전공이랑 부전공이랑 뭐가 다른지 정리해주실 분 있나요?\n\n이수학점, 졸업장 표기 등 차이점이 궁금해요.',
        'comment_count': 15,
        'comments': [
            {'id': 7, 'post_id': 8, 'student_id': None, 'author': '익명', 'text': '복수전공은 36학점, 부전공은 21학점이에요', 'created_at': '2026-01-03'},
            {'id': 8, 'post_id': 8, 'student_id': None, 'author': '익명', 'text': '졸업장에 복수전공은 표기되고 부전공은 안 됩니다', 'created_at': '2026-01-04'},
        ]},
    9: {'id': 9, 'category': 'double', 'board_id': 5, 'student_id': None, 'created_at': '2026-01-14',
        'title': '복수전공 포기하고 부전공으로 전환',
        'content': '복수전공 부담이 커서 부전공으로 바꾸려고 하는데 절차가 어떻게 되나요?\n\n학과사무실에 가야 할까요?',
        'comment_count': 6,
        'comments': []},
}


# =====================================================================
# 라우트
# =====================================================================

@board_bp.route('/')
@board_bp.route('/course')
def list_course():
    """강의평가 목록 페이지"""
    # API 연동 시: GET /api/board/course 결과로 교체
    return render_template('board/board_list_course.html', posts=COURSE_MOCK_POSTS)


@board_bp.route('/community')
def list_community():
    """익명/복학생/부전공/복수전공 목록 페이지"""
    # API 연동 시: GET /api/board/community?cat=<category> 결과로 교체
    category = request.args.get('cat', 'anonymous')
    posts = [p for p in COMMUNITY_MOCK_POSTS if p['category'] == category]
    return render_template('board/board_list_community.html', category=category, posts=posts)


@board_bp.route('/detail/<int:post_id>')
def detail(post_id):
    """강의평가 상세 페이지"""
    # API 연동 시: GET /api/board/course/<post_id> 결과로 교체
    post = COURSE_MOCK_DETAIL.get(post_id)
    if not post:
        post = {'id': post_id, 'subject': '글이 없습니다', 'professor': '', 'semester': '',
                'rating': 0, 'workload': '', 'team_project': '', 'attendance': '',
                'content': '', 'comment_count': 0, 'comments': []}
    return render_template('board/board_detail.html', post=post)


@board_bp.route('/community/detail/<int:post_id>')
def detail_community(post_id):
    """익명/복학생/부전공/복수전공 상세 페이지"""
    # API 연동 시: GET /api/board/community/<post_id> 결과로 교체
    post = COMMUNITY_MOCK_DETAIL.get(post_id)
    if not post:
        post = {'id': post_id, 'category': 'anonymous', 'title': '글이 없습니다',
                'content': '', 'comment_count': 0, 'comments': []}
    category = post['category']
    return render_template('board/board_detail_community.html', post_id=post_id, post=post, category=category)


@board_bp.route('/write/course')
def write_course():
    """강의평가 글쓰기 페이지"""
    return render_template('board/board_write_course.html')


@board_bp.route('/write/community')
def write_community():
    """익명/커뮤니티 글쓰기 페이지"""
    return render_template('board/board_write_community.html')
