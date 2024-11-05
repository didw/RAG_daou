import os
import requests
import streamlit as st

# 환경 변수에서 QUERY_URL 가져오기
QUERY_URL = os.getenv('QUERY_URL', 'http://k8s-default-apigatew-b334012b26-af978099376a3e4b.elb.ap-northeast-2.amazonaws.com/query')

st.title("패션, 트랜드, 여행 등 다양한 주제에 대해 물어보세요!")

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요:"):
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 스피너 표시와 API 요청
    with st.spinner("처리중입니다... 잠시만 기다려 주세요."):
        response = requests.post(QUERY_URL, json={'text': prompt})
        answer = response.json().get('answer')

    # 챗봇 응답 저장 및 표시
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
