# ============ BUILD STAGE ============
FROM python:3.10-slim as builder

WORKDIR /app

# Копируем только файлы зависимостей
COPY requirements.txt .


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

COPY . .

CMD ["uvicorn", "app.main:app","--port", "8000"]