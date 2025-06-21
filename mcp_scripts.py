from mcp.server.fastmcp import FastMCP
import requests
from typing import Optional, Any, List, Dict
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import logging
from pprint import pprint
import re
import asyncio
load_dotenv()

# 로그 설정
def setup_logging(name: str) -> logging.Logger:
    """ 로그 설정
        - logs 디렉토리에 자동 저장
        - 단일 로그 파일 사용
        - UTF-8 인코딩
    """
    # 로그 디렉토리 생성
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 로거 설정
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 핸들러가 중복 추가되는 것을 방지
    if not logger.handlers:
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(
            filename='logs/mcp.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', 
                                                  datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(file_handler)
        
        # 콘솔 출력용 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
        logger.addHandler(console_handler)
    
    return logger

def clean_html_tags(text: str) -> str:
        """HTML 태그와 폰트 태그를 제거하고 깔끔한 텍스트만 반환"""
        if not text:
            return ''
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 여러 공백을 하나로 정리
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

# MCP 서버 설정
mcp = FastMCP("kss_agent_server")
KSS_SERVER = os.getenv("KSS_SERVER")
logger = setup_logging(__name__)
class KSS_Request():
    def __init__(self):
        # 헤더 및 쿠키 파일 로드
        try:
            with open('headers.json', encoding='utf-8') as f:
                self.headers = json.load(f)
            with open('cookies.json', encoding='utf-8') as f:
                self.cookies = json.load(f)
        except Exception as e:
            print(f'헤더 또는 쿠키 파일이 올바르지 않습니다. {e}')
            raise
        
        # KSS api 서버 url 설정
        if str(KSS_SERVER) == '1':
            self.server = 'https://zpdldptmdptm.surplusglobal.com/KSS'            
        elif str(KSS_SERVER) == '2':
            self.server = 'https://kssdev.surplusglobal.com/KSS'            
        else:
            raise Exception('KSS_SERVER 값이 올바르지 않습니다. 1 또는 2를 입력해주세요.')                      
kss_request = KSS_Request()


### Tool 1-1 : (Person ID) Person 상세정보 조회
@mcp.tool()
def kss_account_info_get(person_id: str) -> dict[str, Any]:    
    """KSS Account에 등록된 어카운트 상세정보를 조회합니다.             
    Args:
        person_id: A로 시작하는 어카운트 ID (ex: A142340)                
    """    
    logger.info(f'MCP - Person ID 조회 요청: {person_id.upper()}')
    try: 
        response = requests.get(
            f'{kss_request.server}/AC0180MSearchAll.do', 
            headers=kss_request.headers, 
            cookies=kss_request.cookies, 
            params={'queryDetail1': person_id,'type1':'ACCOUNT_ID/1'},
            timeout=int(os.getenv("MCP_DELAY"))
        )        
        data = {}
        result = response.json()['Data'][0]
        data['company'] = result.get('compnm', '')
        data['company_id'] = result.get('compid', '')
        data['name'] = result.get('personnmdesc', '')
        data['url'] = result.get('urladdr1', '')        
        data['mobile'] = result.get('mobile1', '')
        data['position'] = result.get('positionNm', '')
        data['email'] = result.get('email1', '')
        data['country'] = result.get('countryNm', '')
        data['comment'] = result.get('cmtDescToolTipHtml', '')
        data['account_manager'] = result.get('am', '')
        return {'result': data}
    except Exception as e:
        logger.error(f'MCP - Person ID 조회 오류: {str(e)}')
        return {'error': f'요청 중 오류 발생: {str(e)}'}

### Tool 1-2 : (Company ID) Company 상세정보 조회
@mcp.tool()
def kss_company_info_get(company_id: str) -> dict[str, Any]:
    """KSS Company에 등록된 회사 정보를 조회합니다 반환값에 person_id 가 있습니다..             
    Args:
        company_id: 회사 ID (ex: C12345)                
    """    
    logger.info(f'MCP - 회사 조회 요청: {company_id}')
    try:
        response = requests.get(
            f'{kss_request.server}/AC0180MSearchAll.do',
            headers=kss_request.headers,
            cookies=kss_request.cookies,
            params={'queryDetail1': company_id,'type1':'COMPID/1','queryDetail2':'Company Info','type2':'ACCOUNT_NM/3'},
        )
        data = {}
        results = response.json()['Data']
        for result in results:
            if result['personnmdesc'] =='Company Info' and result['compid'] == company_id.upper():                
                data['company_id'] = result.get('compid', '')
                data['company_name'] = result.get('compnm', '')
                data['url'] = result.get('urladdr1', '')        
                data['tel1'] = result.get('tel1', '')
                data['tel2'] = result.get('tel2', '')
                
                data['email'] = result.get('email1', '')
                data['country'] = result.get('country', '')
                data['address'] = result.get('address', '')
                data['comment'] = clean_html_tags(result.get('cmtDesc', ''))
                data['account_manager'] = result.get('am', '')
                data['CompanyInfoId'] = result.get('id', '')
                return {'result': data}
        return {'error': '회사 정보를 찾을 수 없습니다.'}
    except Exception as e:
        logger.error(f'MCP - Company ID 조회 오류: {str(e)}')
        return {'error': f'요청 중 오류 발생: {str(e)}'}




### Tool 1-2 : (Person ID) 어카운트 코멘트 생성
@mcp.tool()
def kss_account_comment_post(person_id: str, txt: str, date: str = datetime.now().strftime("%Y%m%d"), wtime: str = datetime.now().strftime('%H:%M')) -> dict[str, Any]:
    """KSS Account에 코멘트를 작성합니다.         
    Args:
        person_id: A142340 형식) #앞에 A가 붙어야함
        txt: 작성할 코멘트 내용
        date: 코멘트 날짜 (yyyymmdd 형식, 기본값:현재 날짜)
        wtime: 작성 시간 (HH:MM 형식, 기본값:현재 시간)
    """          
    logger.info(f'MCP - 어카운트 코멘트 작성 요청: {person_id}, {txt}, {date}, {wtime}')
    try:
        data = f'accid={person_id}&newsyn=N&gbn=I&comment={txt}&validdt={date} {wtime}&cmtDataSrcVal={person_id}&cmtDataSrcType=PERSON_ID'        
        response = requests.post(
            f'{kss_request.server}/AC0140PCmtSave.do',
            headers=kss_request.headers,
            cookies=kss_request.cookies,            
            data=data,
            timeout=int(os.getenv("MCP_DELAY"))  # 타임아웃 설정
        )
        if response.status_code == 200:            
            return {'result': '코멘트 작성 성공'}
        else: 
            logger.error(f'MCP - 어카운트 코멘트 작성 실패: {person_id}, {txt}, {date}, {wtime}')
            return {'result': f'코멘트 작성 실패 (상태 코드: {response.status_code})'}
    except Exception as e:
        logger.error(f'MCP - 어카운트 코멘트 작성 오류: {str(e)}')
        return {'error': f'요청 중 오류 발생: {str(e)}'}


### Tool 1-2-1 : (Multiple Person IDs) 어카운트 코멘트 동시 생성
async def _post_comment_async(person_id: str, txt: str, date: str, wtime: str) -> Dict[str, Any]:
    """Helper to post a single comment using asyncio.to_thread to avoid blocking."""
    try:
        data = f'accid={person_id}&newsyn=N&gbn=I&comment={txt}&validdt={date} {wtime}&cmtDataSrcVal={person_id}&cmtDataSrcType=PERSON_ID'
        
        response = await asyncio.to_thread(
            requests.post,
            f'{kss_request.server}/AC0140PCmtSave.do',
            headers=kss_request.headers,
            cookies=kss_request.cookies,
            data=data,
            timeout=int(os.getenv("MCP_DELAY"))
        )
        
        if response.status_code == 200:
            logger.info(f'MCP - 어카운트 코멘트 작성 성공: {person_id}')
            return {'person_id': person_id, 'status': 'success'}
        else:
            logger.error(f'MCP - 어카운트 코멘트 작성 실패: {person_id}, status_code: {response.status_code}')
            return {'person_id': person_id, 'status': 'failed', 'error': f'status code {response.status_code}'}
            
    except Exception as e:
        logger.error(f'MCP - 어카운트 코멘트 작성 오류: {person_id}, error: {str(e)}')
        return {'person_id': person_id, 'status': 'failed', 'error': str(e)}
@mcp.tool()
async def kss_batch_account_comment_post(person_ids: List[str], txt: str) -> dict[str, Any]:
    """KSS Account 여러 개에 대해 동일한 코멘트를 동시에 작성합니다.
    
    Args:
        person_ids: A로 시작하는 어카운트 ID 리스트 (ex: ["A142340", "A142341"])
        txt: 작성할 코멘트 내용
    """
    logger.info(f'MCP - 어카운트 코멘트 동시 작성 요청: {len(person_ids)}개')
    
    now = datetime.now()
    date = now.strftime("%Y%m%d")
    wtime = now.strftime('%H:%M')
    
    tasks = [_post_comment_async(pid, txt, date, wtime) for pid in person_ids]
    results = await asyncio.gather(*tasks)
    
    successful_posts = [r for r in results if r['status'] == 'success']
    failed_posts = [r for r in results if r['status'] == 'failed']
    
    summary = f"총 {len(person_ids)}개 중 {len(successful_posts)}개 성공, {len(failed_posts)}개 실패."
    logger.info(f'MCP - 어카운트 코멘트 동시 작성 완료: {summary}')
    
    return {
        '요약': summary,
        '성공': [r['person_id'] for r in successful_posts],
        '성공person_id': [r['person_id'] for r in successful_posts],
        '실패': failed_posts,
        '실패person_id': [r['person_id'] for r in failed_posts]
    }


### Tool 1-3 : (Person ID) 어카운트 정보 업데이트 (미완성)
@mcp.tool()
def kss_account_info_update(person_id: str,
                            company: str = '',
                            name: str = '',
                            position: str = '',
                            country: str = '',
                            account_manager: str = '',
                            url: str = '',
                            mobile: str = '',
                            email: str = '',
                            comment: str = '',
                            ) -> dict[str, Any]:
    """KSS Account에 어카운트 정보를 업데이트합니다.         
    Args:
        person_id: A142340 형식) #앞에 A가 붙어야함
        company: 회사명
        name: 이름
        position: 직책
        country: 국가
        account_manager: 어카운트 매니저
        url: 웹사이트
        mobile: 전화번호
        email: 이메일
        comment: 코멘트
    """          
    logger.info(f'MCP - 어카운트 정보 업데이트 요청: {person_id}')
    
    try:
        # 기존 정보 조회 먼저
        existing_info_response = kss_account_info_get(person_id)
        if 'error' in existing_info_response:
            return {'error': f'기존 정보 조회 실패: {existing_info_response["error"]}'}
        
        existing_info = existing_info_response['result']
        
        # 업데이트할 데이터 구성 (기존 정보 + 새로운 정보)
        data = {
            'account': person_id,
            # 'copyYn': 'N',
            # 'newsyn': 'N',
            # 'useyn': 'Y',
            # 'rankRadio': 'C',
            # 'gender': 'MR',
            # 'acc_comp_gubun': 'ACC',
            
            # 회사 정보
            # 'repCompNm': company if company else existing_info.get('company', ''),
            # 'regcompnm12': company if company else existing_info.get('company', ''),
            
            # 개인 정보
            'accnm': name if name else existing_info.get('name', ''),
            'position': position if position else existing_info.get('position', ''),
            'amuserid': account_manager if account_manager else existing_info.get('account_manager', ''),
            'webSite': url if url else existing_info.get('url', ''),
            'keyword': comment if comment else existing_info.get('comment', ''),
            
            # 연락처 정보
            'mobile': mobile if mobile else existing_info.get('mobile', ''),
            'mobileType': 'CP',
            'mobilecheck': 'VALID',
            'email': email if email else existing_info.get('email', ''),
            'emailcheck': 'VALID',
            'emailtm': 'on',
            'primaryYn': 'on',
            
            # 주소/국가 정보
            # 'countryNm': country if country else existing_info.get('country', ''),
            
            # 기타 필수 필드들
            # 'department': 'CEM',
            # 'tmYn': 'Y',
            # 'rmYn': 'N',
            # 'emYn': 'N',
            # 'umYn': 'N',
        }

        response = requests.post(
            f'{kss_request.server}/AC0140PAccountSave.do',
            cookies=kss_request.cookies,
            headers=kss_request.headers,
            data=data,
            timeout=int(os.getenv("MCP_DELAY"))
        )
        
        if response.status_code == 200:
            logger.info(f'MCP - 어카운트 정보 업데이트 성공: {person_id}')
            return {'result': '어카운트 정보 업데이트 성공'}
        else:
            logger.error(f'MCP - 어카운트 정보 업데이트 실패: {person_id}, 상태코드: {response.status_code}')
            return {'error': f'업데이트 실패 (상태 코드: {response.status_code})'}
            
    except Exception as e:
        logger.error(f'MCP - 어카운트 정보 업데이트 오류: {str(e)}')
        return {'error': f'요청 중 오류 발생: {str(e)}'}


### Tool 2-1 : (name, company) 어카운트 검색
@mcp.tool()
def kss_account_query_name_company(name: str, company: str = '') -> dict[str, Any]:    
    """
    name, company를 입력하면, KSS 어카운트 검색 결과를 조회합니다.
    등록된 계정이 있을경우 번호. 이름 - 회사 - 어카운트  Person ID 으로 보여줍니다.    

    Args:
        name: 이름 (필수)
        company: 회사명 (선택 - 입력하면 해당 회사 소속만 검색, 입력하지 않으면 전체 검색됨)
               회사명은 영어로 입력 필요.          
    example:
        예상 질문과 AI 응답:
        사용자: "홍길동씨 찾아줘"
        AI: "회사명을 아시면 더 정확한 검색이 가능합니다. 회사명을 알고 계신가요?"
        
        사용자: "삼성전자 홍길동씨 찾아줘"
        AI: name='홍길동', company='Samsung' 으로 바로 검색 실행
        
        사용자: "홍길동씨 찾아줘, 회사는 모르겠어"
        AI: name='홍길동', company='' 으로 전체 검색 실행
    
    Note:
        검색결과가 없을경우  영어로 변경하여 검색할지 사용자에게 물어봅니다.
    """
    logger.info(f'MCP - 어카운트(name, company) 조회 요청: {name}, {company}')
    
    try:
        response = requests.get(
            f'{kss_request.server}/AC0180MSearchAll.do',
            headers=kss_request.headers,
            cookies=kss_request.cookies,
            params={
                'type1': 'ACCOUNT_NM/3^ACCOUNT_LOCAL_NM/3^ACCOUNT_NICK_NM/3',
                'queryDetail1': name,
                'type2': 'COMPNM/3^COMP_LOCAL_NM/3^COMP_NICK_NM/3^COMP_ALIAS/3^NOT_PRIMARY_COMP_ALIAS/3',
                'queryDetail2': company,
                'viewResultCount': '500',
            }
        )           
        
        try:
            results = response.json()['Data'] 
            data = []           
        except Exception as e:       
            return {'result': '검색 결과가 없습니다.'}
        
        for result in results:
            if result['gubun'] == 'PERSON':
                
                data.append({
                    'person_id': result.get('personid', ''),
                    'company': clean_html_tags(result.get('compnm', '')),
                    'company_id': result.get('compid', ''),                
                    'name': result.get('personnmdesc', ''),                
                    'position': result.get('positionNm', ''),              
                    'country': result.get('countryNm', ''),              
                    'account_manager': result.get('am', '')
                })

        return {'search_count': len(data),'result': data}
    except Exception as e:
        logger.error(f'MCP - 어카운트(name, company) 조회 오류: {str(e)}')
        return {'error': f'요청 중 오류 발생: {str(e)}'}
      
### Tool 3-1 : 신규 어카운트 생성
@mcp.tool()
def kss_account_create(name: str = 'Unknown', mobile: str =None, email: str =None, company: str = '', position: str = '', country: str = '', account_manager: str = '', url: str = '', comment: str = '') -> dict[str, Any]:
    """KSS Account에 신규 어카운트를 생성합니다.         
    Args:
        name: 이름
        company: 회사명
        position: 직책
        country: 국가
        account_manager: 어카운트 매니저
        url: 웹사이트
        mobile: 전화번호
        email: 이메일
        comment: 코멘트
    """
    logger.info(f'MCP - 신규 어카운트 생성 요청: {name}, {company}, {position}, {country}, {account_manager}, {url}, {mobile}, {email}, {comment}')
    if mobile:
        mobile_check = requests.post(f'{kss_request.server}/AC0140PMobileCheck.do',cookies=kss_request.cookies,headers=kss_request.headers,data={'mobile': mobile},)
        if mobile_check.text =='"DUPLICATE"':
            return {'error': '동일한 모바일 번호가 KSS 어카운트에 존재합니다.'}
    if email:
        email_check = requests.post(f'{kss_request.server}/AC0140PAutoCompleteEmail.do',cookies=kss_request.cookies,headers=kss_request.headers,data={'searchTerm': email},)
        try:
            result = email_check.json()
            return {'error': f'이미 존재하는 이메일입니다. Person ID: {result[0]["id"]}'}            
        except:
            pass



    return {'result': '이메일 체크 완료'}
     
        

 






if __name__ == "__main__":   
    print("Starting MCP server...")
    mcp.run()

    # result = kss_company_info_get(company_id='c123')
    # pprint(result)
