FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY proto/ proto/
COPY src/ src/
# Generated Python code lives in src/
ENV PYTHONPATH=/app/src
EXPOSE 50051
EXPOSE 50052
WORKDIR /app/src
CMD ["python", "server.py"]
