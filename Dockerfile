# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve Backend & Built Frontend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (e.g. for OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist
COPY frontend/public ./frontend/public

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
