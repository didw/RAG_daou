# Python 3.9 Slim 베이스 이미지 사용
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app.py .

# 포트 노출
EXPOSE 5001

# 컨테이너 실행 시 실행될 명령어
CMD ["python", "app.py"]
