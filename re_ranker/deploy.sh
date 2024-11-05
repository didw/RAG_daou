docker build -t didw/re_ranker:latest .
docker push didw/re_ranker:latest
kubectl rollout restart deployment/re-ranker