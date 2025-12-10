# Estágio de Runtime (Python Slim - Menor e mais seguro)
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema mínimas (libgomp1 é necessário para ONNX/XGBoost)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements da raiz (assumindo build context na raiz)
COPY requirements.txt .

# Instalar libs de produção
# Usamos --no-cache-dir para manter a imagem pequena
RUN pip install --no-cache-dir fastapi uvicorn gunicorn onnxruntime numpy pydantic

# Copiar código da API
COPY api/app.py .

# Nota: O modelo será injetado via Volume na fase de Docker Compose.
# Isso permite trocar o modelo sem rebuildar a imagem inteira.

# Criar usuário não-root por segurança (Best Practice SRE)
RUN useradd -m appuser
USER appuser

# Expor porta
EXPOSE 8000

# Comando de Inicialização Otimizado
# Gunicorn gerencia os processos (Workers)
# Uvicorn gerencia o assincronismo (Threads/Corrotinas)
CMD ["gunicorn", "app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "10", \
     "--keep-alive", "5", \
     "--log-level", "warning"]