docker build -t didw/vector_db:latest .
docker push didw/vector_db:latest
kubectl rollout restart deployment/vector-db