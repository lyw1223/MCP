from mcp.server.fastmcp import FastMCP
import requests
from typing import Optional, Any
from dotenv import load_dotenv
import os
import undetected_chromedriver as uc
from datetime import datetime
import json

load_dotenv()
mcp = FastMCP("kss_agent_server")
KSS_SERVER = os.getenv("KSS_SERVER")

class KSS_Request():
    def __init__(self):
        with open('headers.json', encoding='utf-8') as f:
            self.headers = json.load(f)
        with open('cookies.json', encoding='utf-8') as f:
            self.cookies = json.load(f)
                
        if KSS_SERVER == '2':
            self.server = 'https://kssdev.surplusglobal.com/KSS'            
        elif KSS_SERVER == '1':
            self.server = 'https://zpdldptmdptm.surplusglobal.com/KSS'            
        else:
            raise Exception('KSS_SERVER 값이 올바르지 않습니다. 1 또는 2를 입력해주세요.')
              
kss_request = KSS_Request()


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
    data = f'accid={person_id}&newsyn=N&gbn=I&comment={txt}&validdt={date} {wtime}&cmtDataSrcVal={person_id}&cmtDataSrcType=PERSON_ID'
    
    try:
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
            return {'result': f'코멘트 작성 실패 (상태 코드: {response.status_code})'}
    except Exception as e:
        return {'error': f'요청 중 오류 발생: {str(e)}'}
    

### Tool 2-1 : KSS 어카운트(Person ID) 조회
@mcp.tool()
def kss_account_query_person_id(person_id: str) -> dict[str, Any]:    
    """Person ID를 입력하면, 해당 어카운트 정보를 조회합니다.         
    Args:
        person_id: A142340 형식) #앞에 A가 붙어야함
    """    
    response = requests.get(f'{kss_request.server}/AC0180MSearchAll.do', headers=kss_request.headers, cookies=kss_request.cookies, params={'queryDetail1': person_id,'type1':'ACCOUNT_ID/1'})
    try:        
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
        return {'error': f'요청 중 오류 발생: {str(e)}'}

### Tool 2-2 : KSS 어카운트(name, company) 조회
@mcp.tool()
def kss_account_query_name_company(name: str, company: str = '') -> dict[str, Any]:    
    """name과 company를 입력하면, KSS 어카운트 검색 결과를 조회합니다 여러명이 뜨는대로 조회합니다.         
    Args:
        name: 이름
        company: 회사명 (선택) 회사명은 영어로 입력해주세요.
    """
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

    try:        
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
        return {'error': f'요청 중 오류 발생: {str(e)}'}



if __name__ == "__main__":   
    print("Starting MCP server...")
    mcp.run()

    # kss_account_query_name_company(name='bruce')
    # kss_comment_write(person_id='A142233', txt='test', date='20250618', wtime='00:00')
    # kss_account_query(person_id='A142233')