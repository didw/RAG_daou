from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

app = Flask(__name__)

# 모델 및 토크나이저 로드
MODEL_NAME = 'COCO0414/DNF-bge-m3'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# 청킹 설정
WINDOW_SIZE = 200
OVERLAP = 100

def chunk_text(text, window_size, overlap):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    for i in range(0, len(tokens), window_size - overlap):
        chunk = tokens[i:i + window_size]
        chunks.append(chunk)
        if i + window_size >= len(tokens):
            break
    return chunks

def get_embedding(text):
    # 텍스트를 청킹
    chunks = chunk_text(text, WINDOW_SIZE, OVERLAP)
    embeddings = []
    for chunk in chunks:
        input_ids = torch.tensor([chunk])
        with torch.no_grad():
            outputs = model(input_ids)
            # 마지막 히든 스테이트의 평균값을 사용하여 임베딩 생성
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            embeddings.append(embedding)
    # 청킹된 임베딩의 평균을 구함
    final_embedding = np.mean(embeddings, axis=0)
    return final_embedding.tolist()

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json.get('text')
    if not data:
        return jsonify({'error': 'No text provided'}), 400

    # 임베딩 생성
    embedding = get_embedding(data)

    return jsonify({'embedding': embedding})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
