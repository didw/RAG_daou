from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json.get('text')
    if not data:
        return jsonify({'error': 'No text provided'}), 400

    # 임베딩 로직 (예시로 랜덤 벡터 반환)
    embedding = np.random.rand(768).tolist()

    return jsonify({'embedding': embedding})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
