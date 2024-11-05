docker build -t didw/agent:latest .
docker push didw/agent:latest
kubectl rollout restart deployment/agent