"""
게시판 페이지 라우트
- HTML 템플릿 렌더링만 수행 (API/DB 없음)
- 프론트엔드 페이지 서빙용
"""
from flask import Blueprint, render_template, request

board_bp = Blueprint('board', __name__, url_prefix='/board')

# 커뮤니티 게시판 mock 데이터 (카테고리별 다른 글)
COMMUNITY_MOCK_POSTS = {
    'anonymous': [
        {'id': 1, 'title': '졸업요건 확인하는 거 아시는 분', 'preview': '학교 포털 어디에서 확인하는지 모르겠어요 ㅠㅠ', 'comment_count': 12},
        {'id': 2, 'title': '시험 기출 어디서 구해요?', 'preview': '중간고사 준비하는데 기출문제 구할 곳이 있을까요?', 'comment_count': 5},
        {'id': 3, 'title': '과제 같이 하실 분 구해요', 'preview': '데이터베이스 과제 2번 같이 풀어보실 분 있나요?', 'comment_count': 3},
    ],
    'returning': [
        {'id': 4, 'title': '복학 후 수강신청 꿀팁', 'preview': '2년 만에 복학했는데 수강신청이 너무 달라졌어요. 후배님들 참고하세요.', 'comment_count': 8},
        {'id': 5, 'title': '복학생 학점 인정 문의', 'preview': '군휴학 전에 들었던 과목 학점 인정 받으신 분 계신가요?', 'comment_count': 2},
    ],
    'minor': [
        {'id': 6, 'title': '부전공 심화과목 추천해주세요', 'preview': '경영 부전공 하는데 어떤 과목이 괜찮을까요?', 'comment_count': 7},
        {'id': 7, 'title': '부전공 이수학점 문의', 'preview': '부전공 21학점 이수해야 하는데 18학점만 들었어요. 어떻게 해야 할까요?', 'comment_count': 4},
    ],
    'double': [
        {'id': 8, 'title': '복수전공 vs 부전공 차이', 'preview': '복수전공이랑 부전공이랑 뭐가 다른지 정리해주실 분 있나요?', 'comment_count': 15},
        {'id': 9, 'title': '복수전공 포기하고 부전공으로 전환', 'preview': '복수전공 부담이 커서 부전공으로 바꾸려고 하는데 절차가 어떻게 되나요?', 'comment_count': 6},
    ],
}

# 커뮤니티 상세 mock (id별 본문)
COMMUNITY_MOCK_DETAIL = {
    1: {'title': '졸업요건 확인하는 거 아시는 분', 'content': '학교 포털 어디에서 확인하는지 모르겠어요 ㅠㅠ\n\n졸업요건 체크하는 메뉴가 포털에 있는데 찾기가 어렵네요. 학과사무실에 문의해야 할까요?', 'comment_count': 12, 'comments': [{'author': '익명', 'text': '학생지원팀에 문의해보세요!'}, {'author': '익명', 'text': '포털 로그인 > 학사 > 졸업요건 에 있던데요'}]},
    2: {'title': '시험 기출 어디서 구해요?', 'content': '중간고사 준비하는데 기출문제 구할 곳이 있을까요?\n\n선배님들 도움 부탁드려요.', 'comment_count': 5, 'comments': [{'author': '익명', 'text': '동아리나 스터디에서 공유하는 경우가 많아요'}]},
    3: {'title': '과제 같이 하실 분 구해요', 'content': '데이터베이스 과제 2번 같이 풀어보실 분 있나요?\n\n혼자 하기 어려워서요.', 'comment_count': 3, 'comments': []},
    4: {'title': '복학 후 수강신청 꿀팁', 'content': '2년 만에 복학했는데 수강신청이 너무 달라졌어요. 후배님들 참고하세요.\n\n1. 미리 수강편람 확인\n2. 시간표 미리 짜두기\n3. 당일 새벽에 접속 추천', 'comment_count': 8, 'comments': [{'author': '익명', 'text': '감사합니다!'}, {'author': '익명', 'text': '복학생 우선순위 있나요?'}]},
    5: {'title': '복학생 학점 인정 문의', 'content': '군휴학 전에 들었던 과목 학점 인정 받으신 분 계신가요?\n\n졸업요건에 포함되는지 확인하고 싶어요.', 'comment_count': 2, 'comments': []},
    6: {'title': '부전공 심화과목 추천해주세요', 'content': '경영 부전공 하는데 어떤 과목이 괜찮을까요?\n\n전공이 컴공이라 경영은 처음이에요.', 'comment_count': 7, 'comments': [{'author': '익명', 'text': '마케팅원론 추천해요'}]},
    7: {'title': '부전공 이수학점 문의', 'content': '부전공 21학점 이수해야 하는데 18학점만 들었어요. 어떻게 해야 할까요?\n\n졸업 전에 3학점 더 들어야 하는데요.', 'comment_count': 4, 'comments': []},
    8: {'title': '복수전공 vs 부전공 차이', 'content': '복수전공이랑 부전공이랑 뭐가 다른지 정리해주실 분 있나요?\n\n이수학점, 졸업장 표기 등 차이점이 궁금해요.', 'comment_count': 15, 'comments': [{'author': '익명', 'text': '복수전공은 36학점, 부전공은 21학점이에요'}, {'author': '익명', 'text': '졸업장에 복수전공은 표기되고 부전공은 안 됩니다'}]},
    9: {'title': '복수전공 포기하고 부전공으로 전환', 'content': '복수전공 부담이 커서 부전공으로 바꾸려고 하는데 절차가 어떻게 되나요?\n\n학과사무실에 가야 할까요?', 'comment_count': 6, 'comments': []},
}


@board_bp.route('/')
@board_bp.route('/course')
def list_course():
    """강의평가 목록 페이지"""
    return render_template('board/board_list_course.html')


@board_bp.route('/community')
def list_community():
    """익명/복학생/부전공/복수전공 목록 페이지"""
    category = request.args.get('cat', 'anonymous')
    posts = COMMUNITY_MOCK_POSTS.get(category, COMMUNITY_MOCK_POSTS['anonymous'])
    return render_template('board/board_list_community.html', category=category, posts=posts)


@board_bp.route('/detail/<int:post_id>')
def detail(post_id):
    """강의평가 상세 페이지 (자세히 알아보기)"""
    return render_template('board/board_detail.html', post_id=post_id)


# post_id -> category 매핑 (탭 활성화용)
COMMUNITY_POST_CATEGORY = {
    1: 'anonymous', 2: 'anonymous', 3: 'anonymous',
    4: 'returning', 5: 'returning',
    6: 'minor', 7: 'minor',
    8: 'double', 9: 'double',
}


@board_bp.route('/community/detail/<int:post_id>')
def detail_community(post_id):
    """익명/복학생/부전공/복수전공 상세 페이지 (댓글 가능)"""
    post = COMMUNITY_MOCK_DETAIL.get(post_id)
    if not post:
        post = {'title': '글이 없습니다', 'content': '', 'comment_count': 0, 'comments': []}
    category = COMMUNITY_POST_CATEGORY.get(post_id, 'anonymous')
    return render_template('board/board_detail_community.html', post_id=post_id, post=post, category=category)


@board_bp.route('/write/course')
def write_course():
    """강의평가 글쓰기 페이지"""
    return render_template('board/board_write_course.html')


@board_bp.route('/write/community')
def write_community():
    """익명/커뮤니티 글쓰기 페이지"""
    return render_template('board/board_write_community.html')
