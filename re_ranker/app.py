from flask import Flask, request, jsonify
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/rerank', methods=['POST'])
def rerank():
    documents = request.json.get('documents')
    query = request.json.get('query')

    if not documents:
        return jsonify({'error': 'No documents to re-rank'}), 400

    # 간단한 Re-ranking 로직 (여기서는 임의로 점수를 부여)
    # 실제로는 임베딩 등을 활용하여 유사도를 계산
    scores = np.random.rand(len(documents))
    ranked_docs = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    top_document = ranked_docs[0][0]

    return jsonify({'top_document': top_document})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
