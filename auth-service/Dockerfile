# --- Build stage для кешування залежностей ---
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel -r requirements.txt -w /wheels

# --- Final stage ---
FROM python:3.11-slim
WORKDIR /app

# Копіюємо залежності з build stage
COPY --from=builder /wheels /wheels
COPY requirements.txt .

# Встановлюємо залежності з коліс
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Копіюємо код сервісу
COPY . .

# Запускаємо FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
