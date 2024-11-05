from flask import Flask, request, jsonify
import os
import requests
import logging

app = Flask(__name__)
AGENT_URL = os.getenv('AGENT_URL', 'http://agent-service:5004')

# 기본 로거 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 검색된 문서에 대해 관련성 높은 문서 추출
@app.route('/rerank', methods=['POST'])
def rerank():
    documents = request.json.get('documents')
    query = request.json.get('query')

    if not documents:
        return jsonify({'error': 'No documents to re-rank'}), 400

    # LLM을 이용하여 관련성 높은 문서를 추출
    try:
        response = requests.post(f"{AGENT_URL}/rank_documents", json={'query': query, 'documents': documents})
        response_data = response.json()  # JSON 데이터를 추출
        top_document = response_data.get('top_document')
        logger.debug(f"Top document: {top_document}")
    except Exception as e:
        logger.error(f"Rerank Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'top_document': top_document})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
