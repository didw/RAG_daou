from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 각 모듈의 서비스 URL 설정 (환경 변수로 관리 권장)
EMBEDDING_URL = os.getenv('EMBEDDING_URL', 'http://embedding-service:80/embed')
RETRIEVER_URL = os.getenv('RETRIEVER_URL', 'http://retriever-service:5002/retrieve')
RE_RANKER_URL = os.getenv('RE_RANKER_URL', 'http://re-ranker-service:5003/rerank')
AGENT_URL = os.getenv('AGENT_URL', 'http://agent-service:5004/generate')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('text')
    print(f"User input: {user_input}")

    # 1. Embedding 모듈 호출
    embedding_response = requests.post(EMBEDDING_URL, json={'text': user_input})
    if embedding_response.status_code != 200:
        return jsonify({'error': 'Embedding module error'}), 500
    embedding = embedding_response.json().get('embedding')
    print(f"Embedding: {embedding}")

    # 2. Retriever 모듈 호출
    retrieval_response = requests.post(RETRIEVER_URL, json={'embedding': embedding})
    if retrieval_response.status_code != 200:
        return jsonify({'error': 'Retriever module error'}), 500
    documents = retrieval_response.json().get('documents')
    print(f"Retrieved documents: {documents}")

    # 3. Re-ranker 모듈 호출
    rerank_response = requests.post(RE_RANKER_URL, json={'documents': documents, 'query': user_input})
    if rerank_response.status_code != 200:
        return jsonify({'error': 'Re-ranker module error'}), 500
    top_document = rerank_response.json().get('top_document')
    print(f"Top document: {top_document}")

    # 4. Agent 모듈 호출
    agent_response = requests.post(AGENT_URL, json={'context': top_document, 'query': user_input})
    if agent_response.status_code != 200:
        return jsonify({'error': 'Agent module error'}), 500
    answer = agent_response.json().get('response')
    print(f"Answer: {answer}")

    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
