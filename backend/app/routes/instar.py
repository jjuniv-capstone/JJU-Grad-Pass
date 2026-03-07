"""인스타 로그인 API 라우트"""
import re
import uuid

from flask import Blueprint, request, jsonify, session

from app.services.instar_service import login_and_get_info, _fetch_graduation_info, _fetch_grades, _fetch_courses
import requests as http_requests
from datetime import datetime

instar_bp = Blueprint('instar', __name__)

# 서버사이드 결과 저장 (세션 쿠키 크기 제한 우회)
_result_store = {}


@instar_bp.route('/login', methods=['POST'])
def instar_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "요청 데이터가 없습니다."}), 400

    mem_id = data.get("mem_id", "").strip()
    mem_pw = data.get("mem_pw", "")

    if not mem_id or not mem_pw:
        return jsonify({"success": False, "message": "학번과 비밀번호를 입력해주세요."}), 400

    if not re.match(r'^\d{9}$', mem_id):
        return jsonify({"success": False, "message": "올바른 학번을 입력해주세요."}), 400

    result = login_and_get_info(mem_id, mem_pw)

    mem_pw = None
    del data

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 401


@instar_bp.route('/save-result', methods=['POST'])
def save_result():
    """크롬 확장 프로그램에서 학적정보 결과를 받아 세션에 저장"""
    data = request.get_json()
    if not data or "member" not in data:
        return jsonify({"success": False, "message": "데이터가 없습니다."}), 400

    member = data["member"]
    jsession_id = data.get("jsessionid", "")
    hakbun = member.get("MEM_ID", "")

    graduation = {}
    requirements = []
    grades = []
    courses = []

    # JSESSIONID가 있으면 백엔드에서 졸업이수기준 + 성적 조회
    if jsession_id and hakbun:
        try:
            s = http_requests.Session()
            s.headers.update({"User-Agent": "Mozilla/5.0"})
            s.cookies.set("JSESSIONID", jsession_id, domain="instar.jj.ac.kr")
            graduation, requirements = _fetch_graduation_info(s, hakbun)

            # 입학년도 ~ 현재년도까지 성적 조회
            iphak = member.get("HAKJ_IPHAK_ILJA", "")
            start_year = int(iphak[:4]) if len(iphak) >= 4 else 2021
            current_year = datetime.now().year
            grades = _fetch_grades(s, hakbun, start_year, current_year)

            # 현재 학기 개설강좌 조회
            current_year = datetime.now().year
            current_month = datetime.now().month
            current_semester = 1 if current_month <= 7 else 2
            raw_courses, _ = _fetch_courses(s, hakbun, member, current_year, current_semester)
            for c in raw_courses:
                if not c.get("KYOM_NAME"):
                    continue
                courses.append({
                    "code": c.get("KANG_GWAMOK_CODE", ""),
                    "subject": c.get("KYOM_NAME", ""),
                    "category": c.get("CODE_SNAME", ""),
                    "credits": c.get("KANG_HAKJUM", ""),
                    "professor": c.get("KANG_GYOSU_IRUM", ""),
                    "schedule": c.get("KANG_SIGANGPYO", ""),
                    "enrolled": c.get("KANG_SU_INWON", ""),
                    "capacity": c.get("KANG_SIN_MAX", ""),
                    "year_target": c.get("KAHG_YEAR", ""),
                    "bunban": c.get("KANG_BUNBAN", ""),
                    "method": c.get("METHOD_NM", ""),
                })
        except Exception as e:
            print(f"[데이터 조회 에러] {e}")

    result = {
        "success": True,
        "data": {
            "member": member,
            "graduation": graduation,
            "requirements": requirements,
            "grades": grades,
            "courses": courses,
        },
    }
    # 서버사이드에 저장 (쿠키 크기 제한 우회)
    result_id = str(uuid.uuid4())
    _result_store[result_id] = result
    session["instar_result_id"] = result_id
    return jsonify({"success": True, "message": "저장 완료"})


@instar_bp.route('/result', methods=['GET'])
def instar_result():
    """서버사이드에 저장된 학적정보 반환"""
    result_id = session.get("instar_result_id")
    if not result_id or result_id not in _result_store:
        return jsonify({"success": False, "message": "조회된 데이터가 없습니다. 인스타에서 로그인해주세요."}), 404
    return jsonify(_result_store[result_id])
