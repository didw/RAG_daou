#!/bin/bash

# 필요한 디렉토리 생성
mkdir -p embedding
mkdir -p vector-db
mkdir -p generate
mkdir -p orchestrator
mkdir -p k8s
mkdir -p .github/workflows

# embedding 디렉토리에 파일 생성
touch embedding/app.py
touch embedding/Dockerfile

# vector-db 디렉토리에 파일 생성
touch vector-db/Dockerfile

# generate 디렉토리에 파일 생성
touch generate/app.py
touch generate/Dockerfile

# orchestrator 디렉토리에 파일 생성
touch orchestrator/app.py
touch orchestrator/Dockerfile

# k8s 디렉토리에 파일 생성
touch k8s/deployment.yaml
touch k8s/service.yaml

# .github/workflows 디렉토리에 파일 생성
touch .github/workflows/ci-cd.yaml

# 루트 디렉토리에 README.md 생성
touch README.md

echo "디렉토리 구조가 성공적으로 생성되었습니다."
