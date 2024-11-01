# RAG

## 프로젝트 설정

### 1. Docker 이미지 빌드

각 모듈 디렉토리에서 Docker 이미지를 빌드합니다.

```bash
# Embedding Module
cd embedding
docker build -t didw/embedding:latest .

# Retriever Module
cd ../retriever
docker build -t didw/retriever:latest .

# Re-ranker Module
cd ../re_ranker
docker build -t didw/re_ranker:latest .

# Agent Module
cd ../agent
docker build -t didw/agent:latest .

# API Gateway
cd ../api_gateway
docker build -t didw/api_gateway:latest .

# Vector DB Module
cd ../vector_db
docker build -t didw/vector_db:latest .
```
