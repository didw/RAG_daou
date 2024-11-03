from flask import Flask, request, jsonify
from chromadb import Chroma
from chromadb.api.types import Document, Embedding
from chromadb.api import ChromaClient
import numpy as np
import os

app = Flask(__name__)

# 환경 변수에서 Chroma DB 호스트와 포트 가져오기
chroma_host = os.getenv("CHROMA_DB_HOST", "localhost")
chroma_port = int(os.getenv("CHROMA_DB_PORT", 8001))

# Chroma DB 클라이언트 설정 (외부 Chroma DB 컨테이너와 연결)
client = ChromaClient(f"http://{chroma_host}:{chroma_port}")
vector_store = client.create_collection("documents")

@app.route('/add', methods=['POST'])
def add():
    embedding = request.json.get('embedding')
    document = request.json.get('document')
    if not embedding or not document:
        return jsonify({'error': 'Embedding and document are required'}), 400

    vector_store.add_documents([Document(id=document, embedding=Embedding(np.array(embedding)))])

    return jsonify({'status': 'success'}), 200

@app.route('/query', methods=['POST'])
def query():
    query_embedding = request.json.get('embedding')
    top_k = request.json.get('top_k', 5)
    if not query_embedding:
        return jsonify({'error': 'Embedding is required'}), 400

    query_vector = np.array(query_embedding)
    results = vector_store.query(query_vector, top_k)

    return jsonify({'results': [{'document': result['id'], 'score': result['score']} for result in results]}), 200

@app.route('/clear', methods=['POST'])
def clear():
    vector_store.clear()
    return jsonify({'status': 'success'}), 200

@app.route('/get_size', methods=['GET'])
def get_size():
    size = vector_store.count_documents()
    return jsonify({'size': size}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
