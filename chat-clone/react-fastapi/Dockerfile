# Multi-stage build for React frontend + FastAPI backend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./static

# Serve frontend from FastAPI
RUN echo 'from fastapi.staticfiles import StaticFiles\napp.mount("/", StaticFiles(directory="static", html=True), name="frontend")' >> app.py

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
