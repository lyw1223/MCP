from mcp.server.fastmcp import FastMCP
import requests
from typing import Optional, Any
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import logging
from logging.handlers import RotatingFileHandler

# 로그 설정
def setup_logging(name: str) -> logging.Logger:
    """ 로그 설정
        - logs 디렉토리에 자동 저장
        - 날짜별 로그 파일 생성
        - 파일당 최대 10MB
        - 최대 5개의 백업 파일 유지
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
        file_handler = RotatingFileHandler(
            filename=f'logs/logs_{datetime.now().strftime("%Y%m%d")}.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
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

load_dotenv()
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
        if KSS_SERVER == '1':
            self.server = 'https://zpdldptmdptm.surplusglobal.com/KSS'            
        elif KSS_SERVER == '2':
            self.server = 'https://kssdev.surplusglobal.com/KSS'            
        else:
            raise Exception('KSS_SERVER 값이 올바르지 않습니다. 1 또는 2를 입력해주세요.')        
              
kss_request = KSS_Request()


### Tool 1-1 : (Person ID) 조회
@mcp.tool()
def kss_account_query_person_id(person_id: str) -> dict[str, Any]:    
    """Person ID를 입력하면, 해당 어카운트 상세정보를 조회합니다.         
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

### Tool 1-2 : KSS 어카운트(name, company) 조회
@mcp.tool()
def kss_account_query_name_company(name: str, company: str = '') -> dict[str, Any]:    
    """
    name, company를 입력하면, KSS 어카운트 검색 결과를 조회합니다.
    동명이인이 있을수 있으므로, 사용자가 식별하기 좋게 보여줍니다.    

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
        오류가 발생했을 경우 어떤 오류인지 확인하기 위해 오류 메시지를 출력합니다.
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
                'viewResultCount': '100',
            }
        )           
        data = []
        results = response.json()['Data']
        for result in results:
            data.append({
                'person_id': result.get('personid', ''),
                'company': result.get('compnm', ''),
                'company_id': result.get('compid', ''),                
                'name': result.get('personnmdesc', ''),                
                'position': result.get('positionNm', ''),              
                'country': result.get('countryNm', ''),              
                'account_manager': result.get('am', '')
            })   
        return {'result': data}
    except Exception as e:
        logger.error(f'MCP - 어카운트(name, company) 조회 오류: {str(e)}')
        return {'error': f'요청 중 오류 발생: {str(e)}'}





### Tool 1 : KSS 어카운트 코멘트 작성
@mcp.tool()
def kss_comment_write(person_id: str, txt: str, date: str = datetime.now().strftime("%Y%m%d"), wtime: str = datetime.now().strftime('%H:%M')) -> dict[str, Any]:
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
    


if __name__ == "__main__":   
    print("Starting MCP server...")
    mcp.run()

    # kss_account_query_name_company(name='bruce')
    # kss_comment_write(person_id='A142233', txt='test', date='20250618', wtime='00:00')
    # kss_account_query(person_id='A142233')