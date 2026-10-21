import altair as alt
import pandas as pd
import streamlit as st

NOMES = {"imovel_vazio": "Imóvel vazio", "troca_hidrometro": "Troca de hidrômetro", "sazonalidade": "Sazonalidade",
         "mudanca_de_uso": "Mudança de uso", "sem_causa_identificada": "Sem causa identificada"}
ACERTO, SEM_ACESSO = "Irregularidade encontrada", "Sem acesso ao imóvel"
ORDEM = [ACERTO, *NOMES.values(), SEM_ACESSO]
CORES = ["#2b7a78", "#d1603d", "#e8a33d", "#8c6bb1", "#5b8fd1", "#b0b5bd", "#4d4d4d"]
ESTRATEGIAS = ["Regra antiga", "PoC v1", "PoC v2"]


def _destinos(nome: str, g: dict) -> list[dict]:
    """Todas as visitas de um grupo, em categorias que somam o total de visitas."""
    linhas = [{"estratégia": nome, "destino": ACERTO, "visitas": g["acertos"]},
              {"estratégia": nome, "destino": SEM_ACESSO, "visitas": g["sem_acesso"]}]
    for k, n in g["sem_irregularidade_por_causa"].items():
        linhas.append({"estratégia": nome, "destino": NOMES.get(k, k), "visitas": n})
    return linhas


def render(c) -> None:
    st.title("Para onde o modelo mandou as equipes")
    try:
        r1 = c.arm.ler_json("experimento", f"{c.referencia}_v1")
        r2 = c.arm.ler_json("experimento", f"{c.referencia}_v2")
    except FileNotFoundError:
        st.info(f"Resultado do teste A/B ainda não disponível para {c.referencia}.")
        return
    grupos = [("Regra antiga", r2["regra_antiga"]), ("PoC v1", r1["poc"]), ("PoC v2", r2["poc"])]
    d = pd.DataFrame([x for nome, g in grupos for x in _destinos(nome, g)])
    d["total"] = d["estratégia"].map({nome: g["visitas"] for nome, g in grupos})
    d["ordem"] = d["destino"].map({n: i for i, n in enumerate(ORDEM)})
    d["% das visitas"] = d["visitas"] / d["total"]

    visao = st.radio("Mostrar", ["% das visitas", "visitas"], horizontal=True)
    eixo = alt.Axis(format="%", title="Destino das visitas") if visao == "% das visitas" else alt.Axis(title="Visitas")
    st.altair_chart(alt.Chart(d).mark_bar().encode(
        x=alt.X("estratégia", sort=ESTRATEGIAS, axis=alt.Axis(labelAngle=0, title=None)),
        y=alt.Y(visao, axis=eixo, stack="zero"),
        color=alt.Color("destino", sort=ORDEM, scale=alt.Scale(domain=ORDEM, range=CORES), title=None),
        order=alt.Order("ordem:Q"),
        tooltip=["estratégia", "destino", "visitas", alt.Tooltip("% das visitas", format=".1%")]), width="stretch")

    tab = d.pivot(index="destino", columns="estratégia", values="visitas").reindex(ORDEM).fillna(0).astype(int)[ESTRATEGIAS]
    tab.loc["Total de visitas"] = [g["visitas"] for _, g in grupos]
    st.dataframe(tab.reset_index().rename(columns={"destino": "Destino da visita"}), hide_index=True, width="stretch")

    st.caption("Cada visita termina em um destino: irregularidade encontrada, imóvel sem acesso, ou sem irregularidade "
               "por uma causa conhecida na base sintética. A v2 troca visitas em imóvel vazio e troca de hidrômetro "
               "por visitas com chance real de irregularidade.")
