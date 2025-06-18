# MCP Agent 
Account 조회, 요약, 업데이트 기능을 갖춘 KSS 에이전트를 MCP로 구현

## MCP (Model Context Protocol) 소개
- AI가 외부 데이터의 도구(Tools)에 효과적으로 연결할 수 있는 표준화된 방식
- 특히 다양한 AI 도구의 표준화된 연결로 많이 활용되고 있음
    - **MCP Server**: 사용할 수 있는 도구(tool)를 정의하고 제공하는 역할  
    - **MCP Client**: 정의된 도구를 불러와 사용 (Claude Desktop, Cursor, OpenAI Agents SDK)

## 폴더 구조 및 기능 설명
MCP_Project
├── .env
├── mcp_main.py     # MCP 서버 실행 → streamlit run mcp_main.py
├── mcp_scripts.py   # MCP 서버 기능설정
└── mcp.json        # MCP 서버 경로설정

함수구조
Return Or Raise


## 초기 셋팅
1. 파이썬 가상환경 설정  
    python -m venv venv
    venv\Scripts\activate 

2. 패키지 설치    
    pip install mcp openai-agents streamlit python-dotenv requests

3. env 파일 설정
    KSS_ID = KSSID_입력
    KSS_PW = KSSPW_입력
    KSS_SERVER = 1: Main 2: Dev
    OPENAI_API_KEY= api키_입력
    OPENAI_MODEL= 사용모델_입력    

4. MCP 경로 구성 / 서버 실행에 필요한 **Python 실행 파일 경로**와 **MCP 서버(.py) 스크립트 경로**를 JSON 설정에 입력해야 합니다.
(예: 프로젝트 폴더가 `C:\projects\test\python_mcp_agent`인 경우)
> **주의:** Windows에서는 JSON 문법상 `\` 대신 `\\` (역슬래시 두 번)을 사용해야 합니다.
```json
{
  "mcpServers": {
    "mcp-main": {
      "command": "C:\\projects\\test\\python_mcp_agent\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\projects\\test\\python_mcp_agent\\2_mcp_server.py"
      ]
    }
  }
}
```



