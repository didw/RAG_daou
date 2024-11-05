docker build -t didw/api_gateway:latest .
docker push didw/api_gateway:latest
kubectl rollout restart deployment/api-gateway