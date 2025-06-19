# KSS MCP Server
Account 조회, 요약, 업데이트 기능을 갖춘 KSS 에이전트를 MCP로 구현


# 폴더 구조 및 기능 설명
- .env             # KSS 계정 설정(보안.env파일)
- mcp_main.py      # MCP 서버 실행 → streamlit run mcp_main.py
- mcp_scripts.py   # MCP 서버 기능설정
- mcp.json         # MCP 서버 경로설정
- instructions.txt # MCP 서버 역할설정
- style.css        # MCP 서버 테마설정


# 초기 셋팅
1. 파이썬 가상환경 설정
- python -m venv venv
- venv\Scripts\activate 

2. 패키지 설치    
- pip install mcp openai-agents streamlit python-dotenv requests fastmcp undetected_chromedriver psutil

3. env 파일 설정
- KSS_ID = KSSID_입력
- KSS_PW = KSSPW_입력
- KSS_SERVER = 1: Main 2: Dev
- OPENAI_API_KEY= api키_입력
- OPENAI_MODEL= 사용모델_입력
- MCP_DELAY = MCP 작업 대기시간설정

4. mcp.json 설정 
서버 실행에 필요한 **Python 실행 파일 경로**와 **MCP 서버(.py) 스크립트 경로**를 JSON 설정에 입력해야 합니다.
(예: 프로젝트 폴더가 `C:\projects\test\python_mcp_agent`인 경우)

> **주의:** Windows에서는 JSON 문법상 `\` 대신 `\\` (역슬래시 두 번)을 사용해야 합니다.
```json
{
  "mcpServers": {
    
    "mcp-kss": {
      "command": "C:\\Users\\AsherLim-230703\\Documents\\GitHub\\MCP\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\AsherLim-230703\\Documents\\GitHub\\MCP\\mcp_scripts.py"
      ]
    }, 
       
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\AsherLim-230703\\Desktop\\AI_TABLE"
      ]
    }   
  }
}

```




