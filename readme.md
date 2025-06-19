# KSS MCP Server

Account 조회, 요약, 업데이트 기능을 갖춘 KSS 에이전트를 MCP로 구현

## 시스템 요구사항
- Python 3.11 이상
- Windows 10 이상

## 설치 및 실행 방법

### 1. 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\activate
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
streamlit run mcp_main.py
```

## 프로젝트 구조
```
MCP/
├── mcp_main.py        # 메인 실행 파일
├── mcp_scripts.py     # 스크립트 관련 파일
├── cookies.py         # 쿠키 처리 모듈
├── requirements.txt   # 의존성 패키지 목록
└── README.md          # 프로젝트 문서
```

## mcp.json 설정 
서버 실행에 필요한 **Python 실행 파일 경로**와 **MCP 서버(.py) 스크립트 경로**를 JSON 설정에 입력해야 합니다.

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




