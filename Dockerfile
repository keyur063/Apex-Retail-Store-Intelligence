# Use a lightweight official Python image
FROM python:3.11.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend-only requirements to keep the image small
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Copy the entire project into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the server
CMD ["sh", "-c", "(sleep 5 && echo '\n============================================\n👉 DASHBOARD LINK: http://127.0.0.1:8000 \n============================================\n') & uvicorn src.backend.main:app --host 0.0.0.0 --port 8000"]