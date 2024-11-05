from flask import Flask, request, jsonify
import requests
import os
import logging
import traceback

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

# 서비스 URL 설정 (환경 변수로 관리 권장)
EMBEDDING_URL = os.getenv('EMBEDDING_URL', 'http://embedding-service:80/embed')
RETRIEVER_URL = os.getenv('RETRIEVER_URL', 'http://retriever-service:5002/retrieve')
RE_RANKER_URL = os.getenv('RE_RANKER_URL', 'http://re-ranker-service:5003/rerank')
AGENT_URL = os.getenv('AGENT_URL', 'http://agent-service:5004')

MAX_RETRY = 2  # 최대 재시도 횟수

@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('text')
    logger.debug(f"User input: {user_input}")

    # 1. 사용자 입력 분류 (Agent에게 요청)
    request_type = classify_request(user_input)
    if request_type == "fallback":
        agent_response = requests.post(f"{AGENT_URL}/generate", json={'context': "", 'query': user_input, 'type': request_type})
        if agent_response.status_code != 200:
            logger.error(f"Agent module error: {agent_response.json()}")
            return jsonify({'error': 'Agent module error'}), 500
        answer = agent_response.json().get('response')
        logger.debug(f"Answer: {answer}")
        return jsonify({'answer': answer})
        
    for retry_count in range(MAX_RETRY):
        # 2. Embedding 모듈 호출
        embedding_response = requests.post(EMBEDDING_URL, json={'text': user_input})
        if embedding_response.status_code != 200:
            logger.error(f"Embedding module error: {embedding_response.json()}")
            return jsonify({'error': 'Embedding module error'}), 500
        embedding = embedding_response.json().get('embedding')

        # 3. Retriever 모듈 호출
        retrieval_response = requests.post(RETRIEVER_URL, json={'embedding': embedding})
        if retrieval_response.status_code != 200:
            logger.error(f"Retriever module error: {retrieval_response.json()}")
            return jsonify({'error': 'Retriever module error'}), 500
        documents = retrieval_response.json().get('documents')

        # 4. Re-ranker 모듈 호출
        rerank_response = requests.post(RE_RANKER_URL, json={'documents': documents, 'query': user_input})
        if rerank_response.status_code != 200:
            logger.error(f"Re-ranker module error: {rerank_response.json()}")
            return jsonify({'error': 'Re-ranker module error'}), 500
        top_document = rerank_response.json().get('top_document')

        # 5. 에이전트를 통해 답변 생성
        agent_response = requests.post(f"{AGENT_URL}/generate", json={'context': top_document, 'query': user_input, 'type': request_type})
        if agent_response.status_code != 200:
            logger.error(f"Agent module error: {agent_response.json()}")
            return jsonify({'error': 'Agent module error'}), 500
        answer = agent_response.json().get('response')

        # 6. 적절성 평가
        if is_answer_appropriate(user_input, answer):
            logger.debug(f"Answer: {answer}")
            return jsonify({'answer': answer})

        # 7. Query Rewrite
        user_input = rewrite_query(user_input)
        retry_count += 1
        logger.debug(f"Retrying with modified query: {user_input} (Attempt {retry_count})")
        
        if retry_count >= MAX_RETRY:
            logger.debug(f"Answer: {answer}")
            return jsonify({'answer': answer})


def classify_request(text: str) -> str:
    # Agent에 요청하여 입력 분류
    response = requests.post(f"{AGENT_URL}/classify", json={'text': text})
    if response.status_code != 200:
        return "fallback"
    return response.json().get('classification')

def generate_fallback_message(text: str) -> str:
    response = requests.post(f"{AGENT_URL}/fallback", json={'text': text})
    if response.status_code != 200:
        fallback_message = "지원하지 않는 요청입니다. '트렌드 분석' 또는 '관광지 검색'에 대한 요청을 입력해 주세요."
    return fallback_message

def is_answer_appropriate(user_input: str, answer: str) -> bool:
    # Agent에 적절성 평가 요청
    response = requests.post(f"{AGENT_URL}/evaluate", json={'user_input': user_input, 'answer': answer})
    if response.status_code != 200:
        return False
    return response.json().get('is_appropriate', False)

def rewrite_query(user_input: str) -> str:
    # Agent에 쿼리 수정 요청
    response = requests.post(f"{AGENT_URL}/rewrite", json={'query': user_input})
    if response.status_code != 200:
        return user_input
    return response.json().get('rewritten_query', user_input)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
