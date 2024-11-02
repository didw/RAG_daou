import requests
import os
import pandas as pd

EMBEDDING_URL = os.getenv('EMBEDDING_URL', 'http://aa32403e4f5574a3e9c3e40141b0f950-1325651741.ap-northeast-2.elb.amazonaws.com/embed')
VECTOR_DB_ADD_URL = os.getenv('VECTOR_DB_ADD_URL', 'http://aa35bd1af545b4dceb7f9dc7487917e9-615029480.ap-northeast-2.elb.amazonaws.com/add')
VECTOR_DB_GETSIZE_URL = os.getenv('VECTOR_DB_GETSIZE_URL', 'http://aa35bd1af545b4dceb7f9dc7487917e9-615029480.ap-northeast-2.elb.amazonaws.com/get_size')

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

def check_size():
    response = requests.get(VECTOR_DB_GETSIZE_URL)
    if response.status_code != 200:
        print(f"Vector DB Error: {response.text}")
        return 0  # 기본값으로 0을 반환하여 오류 방지

    size = response.json().get('size')
    print(f"Current size of Vector DB: {size}")
    return size


def main():
    size = check_size()
    print(f"Current size of Vector DB: {size}")
    if size > 0:
        print("Vector DB already contains data. Skipping embedding and storing.")
        return
    
    df = load_data()
    print(df.head())
    documents = df['content'].tolist()

    for doc in documents:
        embed_and_store(doc)

if __name__ == "__main__":
    main()
