# 1. Start from an official Python base image
FROM python:3.10-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy ONLY requirements.txt first (to cache dependencies)
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the backend code
COPY . .

# 6. Expose port 8000 (FastAPI default)
EXPOSE 8000

# 7. Command to run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]