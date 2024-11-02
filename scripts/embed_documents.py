import requests
import os
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import pandas as pd

# 설정
EMBEDDING_URL = os.getenv('EMBEDDING_URL', 'http://aa32403e4f5574a3e9c3e40141b0f950-1325651741.ap-northeast-2.elb.amazonaws.com/embed')
VECTOR_DB_ADD_URL = os.getenv('VECTOR_DB_ADD_URL', 'http://aa35bd1af545b4dceb7f9dc7487917e9-615029480.ap-northeast-2.elb.amazonaws.com/add')

# 모델 및 토크나이저 로드 (임베딩 모듈과 동일하게 설정)
MODEL_NAME = 'bge-small-ko'  # BGE-m3-ko 모델 이름
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

def embed_and_store(document):
    # 임베딩 모듈에 요청하여 임베딩 생성
    response = requests.post(EMBEDDING_URL, json={'text': document})
    if response.status_code != 200:
        print(f"Embedding Error: {response.text}")
        return

    embedding = response.json().get('embedding')
    if not embedding:
        print("No embedding returned")
        return

    # Vector DB에 임베딩과 문서 저장
    add_response = requests.post(VECTOR_DB_ADD_URL, json={'embedding': embedding, 'document': document})
    if add_response.status_code != 200:
        print(f"Vector DB Error: {add_response.text}")
        return

    print("Document embedded and stored successfully")

def load_data():
    # read data/navernews_20240725_20240930.xlsx
    df = pd.read_excel('data/navernews_20240725_20240930.xlsx')
    return df

def main():
    documents = load_data()

    for doc in documents:
        embed_and_store(doc)

if __name__ == "__main__":
    main()
