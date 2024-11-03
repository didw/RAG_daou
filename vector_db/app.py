from flask import Flask, request, jsonify
from chromadb.config import Settings
from chromadb import HttpClient

import numpy as np
import os

app = Flask(__name__)

# 환경 변수에서 Chroma DB 호스트와 포트 가져오기
chroma_host = os.getenv("CHROMA_DB_HOST", "localhost")
chroma_port = int(os.getenv("CHROMA_DB_PORT", 8001))

# Chroma DB 클라이언트 설정 (외부 Chroma DB 컨테이너와 연결)
client = HttpClient(host=chroma_host, port=chroma_port)
collection_name = "documents"

# 컬렉션이 존재하지 않으면 생성
if collection_name not in [col.name for col in client.list_collections()]:
    collection = client.create_collection(name=collection_name)
else:
    collection = client.get_collection(name=collection_name)

@app.route('/add', methods=['POST'])
def add():
    embedding = request.json.get('embedding')
    document = request.json.get('document')
    if not embedding or not document:
        return jsonify({'error': 'Embedding and document are required'}), 400

    collection.add(
        embeddings=[embedding],
        documents=[document],
        ids=[str(collection.count() + 1)]  # 간단한 ID 생성 방식
    )

    return jsonify({'status': 'success'}), 200

@app.route('/query', methods=['POST'])
def query():
    query_embedding = request.json.get('embedding')
    top_k = request.json.get('top_k', 5)
    if not query_embedding:
        return jsonify({'error': 'Embedding is required'}), 400

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return jsonify({'results': [{'document': doc, 'distance': dist} for doc, dist in zip(results['documents'][0], results['distances'][0])]}), 200

@app.route('/clear', methods=['POST'])
def clear():
    collection.delete(where={})
    return jsonify({'status': 'success'}), 200

@app.route('/get_size', methods=['GET'])
def get_size():
    size = collection.count()
    return jsonify({'size': size}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)