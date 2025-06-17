# ============ BUILD STAGE ============
FROM python:3.10-slim as builder

WORKDIR /app


RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============ RUNTIME STAGE ============
FROM python:3.10-slim as runtime

WORKDIR /app


# Копируем venv из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN apt-get update && apt-get install -y curl

COPY . .

CMD ["uvicorn", "app.main:app","--port", "8000"]