# 📊 Performance Benchmarks

Este projeto foi submetido a testes de carga rigorosos usando K6.
Hardware: WSL2 (Windows Subsystem for Linux), 8GB RAM alocada.

## 1. Baseline (Recursos Limitados)
- **Config:** 1.5 CPU, 2GB RAM, 2 Workers
- **Throughput:** ~335 TPS
- **Latência (P95):** ~538ms

## 2. God Mode (Escala Vertical Máxima)
- **Config:** Unlimited CPU (Host), 8GB RAM, 6 Workers
- **Throughput Máximo:** ~918 TPS 🚀
- **Resultado:** Aumento de 2.7x na capacidade de processamento apenas com tuning de infraestrutura.

## Conclusão
O modelo XGBoost quantizado (INT8) servido via FastAPI + Gunicorn demonstrou alta eficiência, capaz de processar quase 1.000 fraudes por segundo em uma única instância de desenvolvimento.