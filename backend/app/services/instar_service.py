"""인스타(inSTAR) 학적정보 스크래핑 서비스"""
import xml.etree.ElementTree as ET

import requests

BASE_URL = "https://instar.jj.ac.kr"
HASH_URL = f"{BASE_URL}/JSP/encryption_sha256.jsp"
XMAIN_URL = f"{BASE_URL}/XMain"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"

HEADERS = {
    "Content-Type": "text/xml",
    "Accept": "application/xml, text/xml, */*",
    "Referer": f"{BASE_URL}/",
    "Origin": BASE_URL,
    "User-Agent": USER_AGENT,
}

NS = {"nx": "http://www.nexacroplatform.com/platform/dataset"}

# --- XML 템플릿 ---

HASH_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">xNoLoginDefaultAction</Parameter>
        <Parameter id="fsp_cmd">execute</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
        <Parameter id="pwd">{pwd}</Parameter>
    </Parameters>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows />
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""

LOGIN_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">JJLogin</Parameter>
        <Parameter id="fsp_cmd">login</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
        <Parameter id="MAX_WRONG_COUNT">5</Parameter>
    </Parameters>
    <Dataset id="ds_cond">
        <ColumnInfo>
            <Column id="SYSTEM_CODE" type="STRING" size="256" />
            <Column id="MEM_ID" type="STRING" size="10" />
            <Column id="MEM_PW" type="STRING" size="256" />
            <Column id="MEM_PW_ENC" type="STRING" size="256" />
            <Column id="MEM_IP" type="STRING" size="20" />
            <Column id="ROLE_GUBUN1" type="STRING" size="256" />
            <Column id="ROLE_GUBUN2" type="STRING" size="256" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="SYSTEM_CODE">INSTAR_WEB</Col>
                <Col id="MEM_ID">{mem_id}</Col>
                <Col id="MEM_PW">{mem_pw}</Col>
                <Col id="MEM_PW_ENC">{mem_pw_enc}</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows />
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
            <Column id="DAEHAK" type="string" size="4000" />
            <Column id="HAKBU" type="string" size="4000" />
            <Column id="HAKGWA" type="string" size="4000" />
            <Column id="HAKJ_YEAR" type="string" size="1" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""

# 졸업이수기준정보 조회 XML
GRADUATION_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">xDefaultAction</Parameter>
        <Parameter id="fsp_cmd">execute</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
    </Parameters>
    <Dataset id="ds_cond">
        <ColumnInfo>
            <Column id="HAKBUN" type="STRING" size="256" />
            <Column id="GPRO_GUBUN" type="STRING" size="256" />
            <Column id="DAEHAK_CODE" type="STRING" size="256" />
            <Column id="HAKBU_CODE" type="STRING" size="256" />
            <Column id="JEONGONG_CODE" type="STRING" size="256" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="HAKBUN">{hakbun}</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">hakjuk_joup:HAKJUK_GPRO_VIEWER_USER_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="USE_INPUT">Y</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">hakjuk_joup:HAKJUK_GPRO_VIEWER_MAJORS_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">hakjuk_joup:HAKJUK_GPRO_VIEWER_SUB_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">hakjuk_joup:HAKJUK_GPRO_VIEWER_GWAMOK_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""

# --- 파싱 함수 ---

def _parse_hash(xml_text):
    """encryption_sha256.jsp 응답에서 해시값 추출"""
    root = ET.fromstring(xml_text)
    for dataset in root.findall(".//nx:Dataset", NS):
        if dataset.get("id") == "ds_pwd":
            for row in dataset.findall(".//nx:Row", NS):
                for col in row.findall("nx:Col", NS):
                    if col.get("id") == "USER_PWD":
                        return col.text
    return None


def _parse_dataset_rows(xml_text, dataset_id):
    """지정한 Dataset의 모든 Row를 리스트로 반환"""
    root = ET.fromstring(xml_text)
    for dataset in root.findall(".//nx:Dataset", NS):
        if dataset.get("id") == dataset_id:
            rows = dataset.findall(".//nx:Row", NS)
            result = []
            for row in rows:
                row_data = {}
                for col in row.findall("nx:Col", NS):
                    row_data[col.get("id")] = col.text or ""
                result.append(row_data)
            return result
    return []


def _parse_member_info(xml_text):
    """로그인 응답에서 학적정보 추출"""
    for ds_id in ("ds_info", "gds_member"):
        rows = _parse_dataset_rows(xml_text, ds_id)
        if rows:
            return rows[0]
    return None


def _check_login_error(xml_text):
    """응답 XML에서 에러 확인"""
    root = ET.fromstring(xml_text)
    error_code = None
    error_msg = None
    for param in root.findall(".//nx:Parameter", NS):
        if param.get("id") == "ErrorCode":
            error_code = param.text
        if param.get("id") == "ErrorMsg":
            error_msg = param.text
    if error_code == "0" and error_msg and "완료" in error_msg:
        return None
    if error_msg and "실패" in error_msg:
        return error_msg
    return None


# --- 메인 함수 ---

def _create_session_and_login(mem_id, mem_pw):
    """인스타 로그인 후 (session, member_info) 반환"""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # 1단계: 메인 페이지 → 쿠키 획득
    session.get(BASE_URL + "/")

    # 2단계: SHA256 해시 획득
    hash_xml = HASH_XML_TEMPLATE.format(pwd=mem_pw)
    hash_resp = session.post(HASH_URL, data=hash_xml.encode("utf-8"), headers=HEADERS)
    hash_resp.raise_for_status()

    mem_pw_enc = _parse_hash(hash_resp.text)
    if not mem_pw_enc:
        return None, None, "비밀번호 암호화에 실패했습니다."

    # 3단계: 로그인
    login_xml = LOGIN_XML_TEMPLATE.format(
        mem_id=mem_id, mem_pw=mem_pw, mem_pw_enc=mem_pw_enc,
    )
    resp = session.post(XMAIN_URL, data=login_xml.encode("utf-8"), headers=HEADERS)
    resp.raise_for_status()

    error = _check_login_error(resp.text)
    if error:
        return None, None, error

    member = _parse_member_info(resp.text)
    return session, member, None


def login_and_get_info(mem_id, mem_pw):
    """로그인 + 학적정보 + 졸업이수기준 조회"""
    session, member, error = _create_session_and_login(mem_id, mem_pw)
    if error:
        return {"success": False, "message": error}
    if not member:
        return {"success": False, "message": "학적정보를 가져올 수 없습니다."}

    # 4단계: 졸업이수기준정보 조회
    grad_xml = GRADUATION_XML_TEMPLATE.format(hakbun=mem_id)
    grad_resp = session.post(XMAIN_URL, data=grad_xml.encode("utf-8"), headers=HEADERS)
    grad_resp.raise_for_status()

    grad_user = _parse_dataset_rows(grad_resp.text, "ds_user")
    grad_sub = _parse_dataset_rows(grad_resp.text, "ds_sub")

    # 졸업 총괄 정보
    graduation = {}
    if grad_user:
        u = grad_user[0]
        graduation = {
            "hakjum_sum": u.get("HAKJUM_SUM", ""),
            "hakjum_grad": u.get("HAKJUM_GRAD", ""),
            "hakjum_need": u.get("HAKJUM_NEED", ""),
            "sugang_sum": u.get("SUGANG_SUM", ""),
            "gijun_year": u.get("GIJUN_YEAR", ""),
        }

    # 이수항목별 현황
    requirements = []
    for row in grad_sub:
        requirements.append({
            "category": row.get("SGSU_GRP_GUBUN", ""),
            "item_name": row.get("SGSU_ITEM_NAME", ""),
            "unit": row.get("SGSU_UNIT", ""),
            "standard": row.get("SGSU_STAND", ""),
            "result": row.get("RESULT_VALUE", ""),
            "passed": row.get("RESULT_YN", ""),
        })

    return {
        "success": True,
        "data": {
            "member": member,
            "graduation": graduation,
            "requirements": requirements,
        },
    }


# 학기별 성적 조회 XML
GRADES_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">xDefaultAction</Parameter>
        <Parameter id="fsp_cmd">execute</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
        <Parameter id="DATE_YY">{year}</Parameter>
        <Parameter id="DATE_HAKGI">{semester}</Parameter>
        <Parameter id="HAKBUN">{hakbun}</Parameter>
    </Parameters>
    <Dataset id="ds_cond">
        <ColumnInfo>
            <Column id="SUNG_YY" type="STRING" size="4" />
            <Column id="SUNG_HAKGI" type="STRING" size="1" />
            <Column id="SUNG_HAKBUN" type="STRING" size="9" />
            <Column id="SUNGJ_GBN" type="STRING" size="1" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="SUNG_YY">{year}</Col>
                <Col id="SUNG_HAKGI">{semester}</Col>
                <Col id="SUNG_HAKBUN">{hakbun}</Col>
                <Col id="SUNGJ_GBN">Y</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1700_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="USE_INPUT">Y</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""


def _fetch_grades(session, hakbun, start_year, current_year):
    """전 학기 성적 조회"""
    all_grades = []

    for year in range(start_year, current_year + 1):
        for semester in (1, 2):
            xml = GRADES_XML_TEMPLATE.format(
                year=year, semester=semester, hakbun=hakbun,
            )
            resp = session.post(XMAIN_URL, data=xml.encode("utf-8"), headers=HEADERS)
            resp.raise_for_status()

            rows = _parse_dataset_rows(resp.text, "ds_list")
            for row in rows:
                if not row.get("KYOM_NAME"):
                    continue
                all_grades.append({
                    "code": row.get("SUNG_GWAMOK_CODE", ""),
                    "year": row.get("SUNG_YY", ""),
                    "semester": row.get("SUNG_HAKGI", ""),
                    "subject": row.get("KYOM_NAME", ""),
                    "category": row.get("CODE_FNAME", ""),
                    "credits": row.get("SUNG_HAKJUM", ""),
                    "score": row.get("SUNG_CHE_JUMSU", ""),
                    "grade": row.get("SUNG_WHAN_JUMSU", ""),
                    "gpa": row.get("SUNG_PUNGJUM", ""),
                    "professor": row.get("INSA_IRUM", ""),
                })

    return all_grades


def _fetch_graduation_info(session, hakbun):
    """졸업이수기준 조회 (공통 로직)"""
    grad_xml = GRADUATION_XML_TEMPLATE.format(hakbun=hakbun)
    grad_resp = session.post(XMAIN_URL, data=grad_xml.encode("utf-8"), headers=HEADERS)
    grad_resp.raise_for_status()

    grad_user = _parse_dataset_rows(grad_resp.text, "ds_user")
    grad_sub = _parse_dataset_rows(grad_resp.text, "ds_sub")

    graduation = {}
    if grad_user:
        u = grad_user[0]
        graduation = {
            "hakjum_sum": u.get("HAKJUM_SUM", ""),
            "hakjum_grad": u.get("HAKJUM_GRAD", ""),
            "hakjum_need": u.get("HAKJUM_NEED", ""),
            "sugang_sum": u.get("SUGANG_SUM", ""),
            "gijun_year": u.get("GIJUN_YEAR", ""),
        }

    requirements = []
    for row in grad_sub:
        requirements.append({
            "category": row.get("SGSU_GRP_GUBUN", ""),
            "item_name": row.get("SGSU_ITEM_NAME", ""),
            "unit": row.get("SGSU_UNIT", ""),
            "standard": row.get("SGSU_STAND", ""),
            "result": row.get("RESULT_VALUE", ""),
            "passed": row.get("RESULT_YN", ""),
        })

    return graduation, requirements


# 개설강좌 조회 XML
COURSES_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">xDefaultAction</Parameter>
        <Parameter id="fsp_cmd">execute</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
    </Parameters>
    <Dataset id="ds_cond">
        <ColumnInfo>
            <Column id="SUGA_YY" type="STRING" size="4" />
            <Column id="SUGA_HAKGI" type="STRING" size="1" />
            <Column id="SUGA_HAKBUN" type="STRING" size="9" />
            <Column id="SUGA_DAEHAK" type="STRING" size="10" />
            <Column id="SUGA_HAKBU" type="STRING" size="10" />
            <Column id="SUGA_JEONGONG" type="STRING" size="10" />
            <Column id="SUGA_JUYA" type="STRING" size="1" />
            <Column id="SUGA_KANGNO" type="STRING" size="10" />
            <Column id="SUGA_KYOYANG" type="STRING" size="5" />
            <Column id="GWAMOK_NM" type="STRING" size="256" />
            <Column id="SUGA_YEAR" type="STRING" size="256" />
            <Column id="KYOM_SUN01" type="STRING" size="256" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="SUGA_YY">{year}</Col>
                <Col id="SUGA_HAKGI">{semester}</Col>
                <Col id="SUGA_HAKBUN">{hakbun}</Col>
                <Col id="SUGA_DAEHAK">{daehak}</Col>
                <Col id="SUGA_HAKBU">{hakbu}</Col>
                <Col id="SUGA_JEONGONG">{jeongong}</Col>
                <Col id="SUGA_JUYA">1</Col>
                <Col id="GWAMOK_NM" />
                <Col id="SUGA_YEAR" />
                <Col id="KYOM_SUN01" />
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1500_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1500_R02</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1500_R03</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""


def _fetch_courses(session, hakbun, member, year, semester):
    """개설강좌 조회"""
    daehak = member.get("HAKJ_DAEHAK", "")
    hakbu = member.get("HAKJ_HAKBU", "")
    jeongong = member.get("HAKJ_HAKGWA", "")

    xml = COURSES_XML_TEMPLATE.format(
        year=year, semester=semester, hakbun=hakbun,
        daehak=daehak, hakbu=hakbu, jeongong=jeongong,
    )
    resp = session.post(XMAIN_URL, data=xml.encode("utf-8"), headers=HEADERS)
    resp.raise_for_status()

    all_rows = []
    for ds_id in ("ds_list", "ds_list2", "ds_list3"):
        rows = _parse_dataset_rows(resp.text, ds_id)
        if rows:
            all_rows.extend(rows)

    return all_rows


# 시간표 조회 XML
TIMETABLE_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">xDefaultAction</Parameter>
        <Parameter id="fsp_cmd">execute</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
    </Parameters>
    <Dataset id="ds_cond">
        <ColumnInfo>
            <Column id="SUGA_YY" type="STRING" size="4" />
            <Column id="SUGA_HAKGI" type="STRING" size="1" />
            <Column id="SUGA_HAKBUN" type="STRING" size="9" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="SUGA_YY">{year}</Col>
                <Col id="SUGA_HAKGI">{semester}</Col>
                <Col id="SUGA_HAKBUN">{hakbun}</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1400_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="USE_INPUT">Y</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1400_R02</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">uem:UEM_1400_R03</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""


def _fetch_timetable(session, hakbun, year, semester):
    """시간표 조회"""
    xml = TIMETABLE_XML_TEMPLATE.format(
        year=year, semester=semester, hakbun=hakbun,
    )
    resp = session.post(XMAIN_URL, data=xml.encode("utf-8"), headers=HEADERS)
    resp.raise_for_status()

    # ds_list: 시간표 격자 (교시별 월~토 과목명)
    grid_rows = _parse_dataset_rows(resp.text, "ds_list")
    grid = []
    for row in grid_rows:
        grid.append({
            "period": row.get("SIGA_GYOSI", ""),
            "mon": row.get("WEEK1", ""),
            "tue": row.get("WEEK2", ""),
            "wed": row.get("WEEK3", ""),
            "thu": row.get("WEEK4", ""),
            "fri": row.get("WEEK5", ""),
            "sat": row.get("WEEK6", ""),
            "time": row.get("VIEW_TIME", ""),
        })

    # ds_list2: 수강 과목 목록
    subject_rows = _parse_dataset_rows(resp.text, "ds_list2")
    subjects = []
    for row in subject_rows:
        subjects.append({
            "code": row.get("KANG_GWAMOK_CODE", ""),
            "bunban": row.get("KANG_BUNBAN", ""),
            "name": row.get("KANG_NAME", ""),
            "professor": row.get("GYOSU", ""),
        })

    return {"grid": grid, "subjects": subjects}


def fetch_info_with_cookies(cookies):
    """크롬 확장 프로그램에서 받은 쿠키로 학적정보 + 졸업이수기준 조회"""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # 쿠키 설정
    for name, value in cookies.items():
        session.cookies.set(name, value, domain="instar.jj.ac.kr")

    # 세션 체크 + 학적정보 조회 (로그인 후 메인 로드와 동일한 요청)
    session_check_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="fsp_action">xDefaultAction</Parameter>
        <Parameter id="fsp_cmd">execute</Parameter>
        <Parameter id="GV_USER_ID" />
        <Parameter id="GV_IP_ADDRESS" />
        <Parameter id="GV_LANGUAGE">KO</Parameter>
        <Parameter id="fsp_logId">all</Parameter>
    </Parameters>
    <Dataset id="fsp_ds_cmd">
        <ColumnInfo>
            <Column id="TX_NAME" type="STRING" size="100" />
            <Column id="TYPE" type="STRING" size="10" />
            <Column id="SQL_ID" type="STRING" size="200" />
            <Column id="KEY_SQL_ID" type="STRING" size="200" />
            <Column id="KEY_INCREMENT" type="INT" size="10" />
            <Column id="CALLBACK_SQL_ID" type="STRING" size="200" />
            <Column id="INSERT_SQL_ID" type="STRING" size="200" />
            <Column id="UPDATE_SQL_ID" type="STRING" size="200" />
            <Column id="DELETE_SQL_ID" type="STRING" size="200" />
            <Column id="SAVE_FLAG_COLUMN" type="STRING" size="200" />
            <Column id="USE_INPUT" type="STRING" size="1" />
            <Column id="USE_ORDER" type="STRING" size="1" />
            <Column id="KEY_ZERO_LEN" type="INT" size="10" />
            <Column id="BIZ_NAME" type="STRING" size="100" />
            <Column id="PAGE_NO" type="INT" size="10" />
            <Column id="PAGE_SIZE" type="INT" size="10" />
            <Column id="READ_ALL" type="STRING" size="1" />
            <Column id="EXEC_TYPE" type="STRING" size="2" />
            <Column id="EXEC" type="STRING" size="1" />
            <Column id="FAIL" type="STRING" size="1" />
            <Column id="FAIL_MSG" type="STRING" size="200" />
            <Column id="EXEC_CNT" type="INT" size="1" />
            <Column id="MSG" type="STRING" size="200" />
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="TYPE">N</Col>
                <Col id="SQL_ID">com_juis:COM_SESSION_CHK_R01</Col>
                <Col id="KEY_INCREMENT">0</Col>
                <Col id="KEY_ZERO_LEN">0</Col>
                <Col id="EXEC_TYPE">B</Col>
                <Col id="EXEC_CNT">0</Col>
            </Row>
        </Rows>
    </Dataset>
    <Dataset id="gds_member">
        <ColumnInfo>
            <Column id="MEM_GUBN" type="string" size="1" />
            <Column id="MEM_ID" type="string" size="9" />
            <Column id="MEM_NM" type="string" size="60" />
        </ColumnInfo>
        <Rows />
    </Dataset>
</Root>"""

    resp = session.post(XMAIN_URL, data=session_check_xml.encode("utf-8"), headers=HEADERS)
    resp.raise_for_status()

    member = _parse_member_info(resp.text)
    if not member:
        return {"success": False, "message": "세션이 만료되었습니다. 다시 로그인해주세요."}

    hakbun = member.get("MEM_ID", "")
    if not hakbun:
        return {"success": False, "message": "학번을 확인할 수 없습니다."}

    graduation, requirements = _fetch_graduation_info(session, hakbun)

    return {
        "success": True,
        "data": {
            "member": member,
            "graduation": graduation,
            "requirements": requirements,
        },
    }
