FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ollama 运行在宿主机，容器内通过 host.docker.internal 访问
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV OLLAMA_MODEL=gpt-oss:120b

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
