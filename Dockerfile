FROM --platform=linux/arm64 python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Отдельный слой для зависимостей: повторная сборка после правки кода быстрее.
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

# Работает, если в проекте есть main.py с поддержкой --help.
CMD ["python", "main.py", "--help"]
