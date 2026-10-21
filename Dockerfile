FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY . .

# Base sintetica + pipeline gerados na imagem (modo offline, sem chave de API).
# Escala reduzida para o build ser rapido; mude ESCALA para 500000 para o caso completo.
ARG ESCALA=50000
RUN python -m scripts.gerar_base --escala ${ESCALA} --semente 42 \
 && python -m src.pipeline --mes 2026-08 --formulacao v1 \
 && python -m src.pipeline --mes 2026-08 --formulacao v2 \
 && python -m src.experiment --mes 2026-08 --formulacao v1 \
 && python -m src.experiment --mes 2026-08 --formulacao v2

ENV PORT=8080
EXPOSE 8080
CMD streamlit run app/painel.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
