from mcp.server.fastmcp import FastMCP
from selenium.webdriver.common.by import By
import time
import requests
from typing import Optional, Any
from dotenv import load_dotenv
import psutil
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
              
                   
### Tool 1 : KSS 계정 코멘트 작성
@mcp.tool()
def kss_comment_write(person_id: str, txt: str, date: str = datetime.now().strftime("%Y%m%d"), wtime: str = '00:00') -> dict[str, Any]:
    """KSS Account에 코멘트를 작성합니다.         
    Args:
        person_id: A142340 형식) #앞에 A가 붙어야함
        txt: 작성할 코멘트 내용
        date: 코멘트 날짜 (yyyymmdd 형식, 기본값:오늘 날짜)
        wtime: 작성 시간 (HH:MM 형식, 기본값 00:00)
    """      
    kss_request = KSS_Request()
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
    

def kss_account_query(person_id: str) -> dict[str, Any]:
    """KSS Account을 조회합니다.         
    Args:
        person_id: A142340 형식) #앞에 A가 붙어야함
    """
    kss_request = KSS_Request()
    response = requests.get(f'{kss_request.server}/AC0180MSearchAll.do', headers=kss_request.headers, cookies=kss_request.cookies, params={'queryDetail1': person_id,'type1':'ACCOUNT_ID/1'})
    if response.status_code == 200:
        data = {}
        result = response.json()['Data'][0]
        data['name'] = result['name']

        return {'result': data}
    else:
        return {'error': f'요청 중 오류 발생: {response.status_code}'}

if __name__ == "__main__":   
    # print("Starting MCP server...")
    # mcp.run()
    # kss_comment_write(person_id='A142233', txt='test', date='20250618', wtime='00:00')
    kss_account_query(person_id='A142233')