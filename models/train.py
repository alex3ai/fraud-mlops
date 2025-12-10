import time
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
# Import do conversor XGBoost
from onnxmltools import convert_xgboost
# Import de tipos corretos
from onnxmltools.convert.common.data_types import FloatTensorType

# Configurações
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)
N_FEATURES = 30

def generate_data(n_samples=100_000):
    """Gera dados sintéticos realistas: 99.5% normais, 0.5% fraudes"""
    print("🎲 Gerando dados sintéticos...")
    np.random.seed(42)
    
    # Normais
    n_normal = int(n_samples * 0.995)
    X_normal = np.random.randn(n_normal, N_FEATURES)
    y_normal = np.zeros(n_normal)
    
    # Fraudes
    n_fraud = n_samples - n_normal
    X_fraud = np.random.randn(n_fraud, N_FEATURES) * 2 + 4
    y_fraud = np.ones(n_fraud)
    
    X = np.vstack([X_normal, X_fraud]).astype(np.float32)
    y = np.hstack([y_normal, y_fraud])
    
    # Shuffle
    idx = np.random.permutation(len(y))
    return X[idx], y[idx]

def train_pipeline():
    # 1. Dados
    X, y = generate_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    
    # 2. Treino XGBoost
    print("🚀 Treinando XGBoost...")
    model = xgb.XGBClassifier(
        max_depth=6, 
        n_estimators=100, 
        learning_rate=0.1, 
        n_jobs=-1,
        tree_method="hist"
    )
    model.fit(X_train, y_train)
    
    # Validação
    score = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"📊 AUC-ROC: {score:.4f}")

    # 3. Conversão para ONNX
    print("🔄 Convertendo para ONNX (Otimizado)...")
    initial_type = [('float_input', FloatTensorType([None, N_FEATURES]))]
    
    # Opset 12 é muito estável para XGBoost
    onx = convert_xgboost(model, initial_types=initial_type, target_opset=12)
    
    # Salvamos com o nome "_quant" para manter compatibilidade com o resto do tutorial
    # Mesmo sem ser int8, o ONNX Runtime em C++ garantirá a performance.
    final_path = MODEL_DIR / "fraud_model_quant.onnx"
    
    with open(final_path, "wb") as f:
        f.write(onx.SerializeToString())

    size_mb = final_path.stat().st_size / (1024 * 1024)
    print(f"✅ Modelo ONNX pronto: {final_path} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    train_pipeline()