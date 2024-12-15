# 1. Python 3.11-slim 이미지 사용
FROM python:3.11-slim

# 2. 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 파일 복사
COPY requirements.txt /app/requirements.txt

# 5. Python 패키지 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# 6. 애플리케이션 코드 복사
COPY . /app

# 7. Slack Bolt 앱 실행
CMD ["python", "main.py"]
