# RAG

### 1. Docker 이미지 빌드

각 모듈 디렉토리에서 Docker 이미지를 빌드 및 배포합니다.

```bash
# Embedding Module
cd embedding
docker build -t didw/embedding:latest .
docker push didw/embedding:latest

# Retriever Module
cd ../retriever
docker build -t didw/retriever:latest .
docker push didw/retriever:latest

# Re-ranker Module
cd ../re_ranker
docker build -t didw/re_ranker:latest .
docker push didw/re_ranker:latest

# Agent Module
cd ../agent
docker build -t didw/agent:latest .
docker push didw/agent:latest

# API Gateway
cd ../api_gateway
docker build -t didw/api_gateway:latest .
docker push didw/api_gateway:latest

# Vector DB Module
cd ../vector_db
docker build -t didw/vector_db:latest .
docker push didw/vector_db:latest
```

### 2. k8s 클러스터 설정

```bash
# k8s 클러스터 설정
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### 3. 데이터 삽입

```bash
python script/embed_documents.py
```

### 4. 테스트 쿼리

```bash
python script/test_query.py
```

### 5. 챗봇 URL

https://chatbot-rag-jyyang.streamlit.app/
