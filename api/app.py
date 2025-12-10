import os
import time
import logging
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Configuração de Logs Minimalista
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger("api")

# Variáveis Globais para o Modelo
model_session = None
input_name = None

# ==========================================
# LIFESPAN (Carregamento Eficiente)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega o modelo ONNX na memória apenas uma vez na inicialização"""
    global model_session, input_name
    
    # Define o caminho padrão, mas aceita variável de ambiente
    model_path = os.getenv("MODEL_PATH", "models/fraud_model_quant.onnx")
    logger.info(f"Carregando modelo de: {model_path}")
    
    # Tweak de Performance ONNX:
    # intra_op_num_threads=1: CRÍTICO! Evita que o ONNX brigue por CPU com o Gunicorn
    sess_options = ort.SessionOptions()
    sess_options.intra_op_num_threads = 1
    sess_options.inter_op_num_threads = 1
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    
    try:
        model_session = ort.InferenceSession(model_path, sess_options)
        input_name = model_session.get_inputs()[0].name
        logger.info("✅ Modelo carregado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro fatal ao carregar modelo: {e}")
        # Não iniciamos a API se o modelo falhar
        raise e
        
    yield
    
    # Cleanup (se necessário)
    model_session = None

# Inicializar App
app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

# ==========================================
# SCHEMAS
# ==========================================
class PredictionRequest(BaseModel):
    features: list[float]

class PredictionResponse(BaseModel):
    fraud_score: float
    is_fraud: bool
    inference_time_ms: float

# ==========================================
# ENDPOINTS
# ==========================================
@app.get("/health")
async def health_check():
    """Health check ultrarrápido para o Kubernetes/Load Balancer"""
    if model_session is None:
        return {"status": "starting"}
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest):
    """
    Endpoint de inferência crítica.
    """
    start_time = time.perf_counter()
    
    # 1. Preparar entrada (NumPy array float32 direto)
    # Convertemos a lista Python para Tensor NumPy
    input_tensor = np.array([payload.features], dtype=np.float32)
    
    # 2. Inferência ONNX
    outputs = model_session.run(None, {input_name: input_tensor})
    
    # 3. Pós-processamento
    # ONNX retorna uma lista de mapas [{0: prob, 1: prob}]. Pegamos a prob de fraude (1).
    try:
        # A estrutura de saída do XGBoost/ONNX pode variar. 
        # Geralmente outputs[1] é a lista de probabilidades (dicionários).
        probs = outputs[1][0] # Primeiro sample
        fraud_prob = float(probs[1]) # Probabilidade da classe 1
    except:
        # Fallback caso a estrutura seja diferente (array puro)
        fraud_prob = float(outputs[0][0]) 

    duration = (time.perf_counter() - start_time) * 1000
    
    return {
        "fraud_score": fraud_prob,
        "is_fraud": fraud_prob > 0.5,
        "inference_time_ms": round(duration, 2)
    }