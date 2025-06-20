import streamlit as st
import sys
import asyncio
import json
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
import os
import openai
import base64


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

    
# Windows 호환성오류 방지
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# MCP 서버 설정
async def setup_mcp_servers():
    servers = []
    
    # mcp.json 파일에서 설정 읽기
    with open('mcp.json', 'r') as f:
        config = json.load(f)
    
    # mcp-kss 서버의 파이썬 경로를 현재 실행중인 파이썬으로 지정
    if 'mcp-kss' in config.get('mcpServers', {}):
        config['mcpServers']['mcp-kss']['command'] = sys.executable

    # 구성된 MCP 서버들을 순회
    for server_name, server_config in config.get('mcpServers', {}).items():
        mcp_server = MCPServerStdio(
            params={
                "command": server_config.get("command"),
                "args": server_config.get("args", []),
                "env": os.environ
            },
            cache_tools_list=True,
            client_session_timeout_seconds= int(os.getenv("MCP_DELAY"))            
        )
        await mcp_server.connect()
        servers.append(mcp_server)            
    return servers

# 에이전트 설정
async def setup_agent():
    # 서버가 이미 존재하는지 확인하고, 없으면 생성
    mcp_servers = await setup_mcp_servers()
    
    agent = Agent(
        name="Assistant",
        instructions=open('instructions.txt', 'r', encoding='utf-8').read(),
        model= os.getenv("OPENAI_MODEL"),
        mcp_servers= mcp_servers
    )
    return agent,mcp_servers


# 메시지 처리
async def process_user_message():
    try:
        agent, mcp_servers = await setup_agent()
        messages = st.session_state.chat_history

        result = Runner.run_streamed(agent, input=messages)

        response_text = ""
        placeholder = st.empty()

        async for event in result.stream_events():           
            # LLM 응답 토큰 스트리밍
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                response_text += event.data.delta or ""
                with placeholder.container():
                    with st.chat_message("assistant"):
                        st.markdown(response_text)

            # 도구 이벤트와 메시지 완료 처리
            elif event.type == "run_item_stream_event":
                item = event.item

                if item.type == "tool_call_item":
                    tool_name = item.raw_item.name
                    st.toast(f"🛠 도구 활용: `{tool_name}`")
          

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_text
        })
        # 명시적 종료 (streamlit에서 비동기 처리 오류 방지)
        for server in mcp_servers:
            await server.__aexit__(None, None, None)
    except asyncio.CancelledError:
        pass

# Streamlit UI 메인
def main():        
    st.set_page_config(page_icon="🔷")

    # style.css 적용
    with open("style.css",encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # 로고 표시
    st.markdown(
        f'<div style="text-align: left;"><img src="data:image/png;base64,{base64.b64encode(open("surplusglobal_logo.png", "rb").read()).decode()}" width="300"></div>',
        unsafe_allow_html=True
    )        

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    
    st.title(f"{os.getenv('KSS_ID').upper()}님, 안녕하세요!")
    st.divider()   
    st.caption(f"Account 생성, 업데이트, 삭제, 조회 등 요청해주세요! - AI Model: ({os.getenv('OPENAI_MODEL')})")
    if os.getenv('KSS_SERVER') == '1':
        st.caption("⚠️ 주의: 메인 서버에서 실행 중입니다.")
    elif os.getenv('KSS_SERVER') == '2':
        st.caption("ℹ️ 알림: 개발 서버에서 실행 중입니다. 속도가 느릴 수 있습니다.")

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 사용자 입력 처리
    user_input = st.chat_input("오늘 어떤 도움을 드릴까요?")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        # 비동기 응답 처리
        with st.spinner("AI가 답변을 작성 중입니다..."):
            try:
                asyncio.run(process_user_message())
            except openai.APIError as e:
                st.error(f"오류 발생: {e}")
            except Exception as e:
                st.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
