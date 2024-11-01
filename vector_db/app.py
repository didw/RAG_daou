from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# 간단한 인메모리 벡터 저장소
vector_store = []

@app.route('/add', methods=['POST'])
def add():
    embedding = request.json.get('embedding')
    document = request.json.get('document')
    if not embedding or not document:
        return jsonify({'error': 'Embedding and document are required'}), 400

    vector_store.append({'embedding': np.array(embedding), 'document': document})
    return jsonify({'status': 'success'}), 200

@app.route('/query', methods=['POST'])
def query():
    query_embedding = request.json.get('embedding')
    top_k = request.json.get('top_k', 5)
    if not query_embedding:
        return jsonify({'error': 'Embedding is required'}), 400

    query_vector = np.array(query_embedding)
    similarities = []
    for item in vector_store:
        score = np.dot(query_vector, item['embedding'])
        similarities.append({'document': item['document'], 'score': score})

    # 유사도에 따라 정렬
    similarities.sort(key=lambda x: x['score'], reverse=True)
    top_results = similarities[:top_k]

    return jsonify({'results': top_results}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
