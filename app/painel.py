"""Painel de apresentação da PoC (Streamlit). Camada fina: só lê as saídas do pipeline pela
camada de armazenamento e chama funções públicas dos componentes. Sem regra de negócio aqui.

    streamlit run app/painel.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # raiz do repo, para importar `src`

import streamlit as st  # noqa: E402

from app.comum import barra_lateral  # noqa: E402
from app.paginas import (contratos_pendencias, experimento_v1, experimento_v2, fila_do_dia,  # noqa: E402
                         para_onde, rotulos, simulador, visao_geral)

st.set_page_config(page_title="Águas do Vale · PoC", layout="wide")

PAGINAS = {
    "Visão geral": visao_geral,
    "Fila do dia": fila_do_dia,
    "Teste A/B · PoC v1": experimento_v1,
    "Teste A/B · PoC v2": experimento_v2,
    "Para onde o modelo mandou as equipes": para_onde,
    "Simulador de restrições": simulador,
    "Rótulos": rotulos,
    "Contratos e pendências": contratos_pendencias,
}

sel = st.sidebar.radio("Página", list(PAGINAS))
ctx = barra_lateral()
if ctx is None:
    st.warning("Nenhuma execução encontrada. Rode `python -m src.pipeline` antes de abrir o painel.")
else:
    PAGINAS[sel].render(ctx)
