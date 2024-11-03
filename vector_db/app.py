from flask import Flask, request, jsonify
import chromadb
from chromadb.config import Settings
import os

app = Flask(__name__)

# ChromaDB 서버의 서비스 주소와 포트를 환경 변수에서 가져오기
chroma_host = os.getenv("CHROMA_DB_HOST", "chroma-db-service")
chroma_port = int(os.getenv("CHROMA_DB_PORT", 8001))

# 클라이언트 설정
client = chromadb.Client(Settings(
    chroma_server_host=chroma_host,
    chroma_server_grpc_port=chroma_port,
))

vector_store = client.get_or_create_collection(name="documents")

@app.route('/add', methods=['POST'])
def add():
    embedding = request.json.get('embedding')
    document = request.json.get('document')
    if embedding is None or document is None:
        return jsonify({'error': 'Embedding and document are required'}), 400

    vector_store.add(
        documents=[document],
        embeddings=[embedding],
        ids=[document]
    )

    return jsonify({'status': 'success'}), 200

@app.route('/query', methods=['POST'])
def query():
    query_embedding = request.json.get('embedding')
    top_k = request.json.get('top_k', 5)
    if query_embedding is None:
        return jsonify({'error': 'Embedding is required'}), 400

    results = vector_store.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # 결과 처리
    response = []
    for ids, distances in zip(results['ids'], results['distances']):
        for id_, distance in zip(ids, distances):
            response.append({'document': id_, 'score': distance})

    return jsonify({'results': response}), 200

@app.route('/clear', methods=['POST'])
def clear():
    vector_store.delete()
    return jsonify({'status': 'success'}), 200

@app.route('/get_size', methods=['GET'])
def get_size():
    size = vector_store.count()
    return jsonify({'size': size}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
