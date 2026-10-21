import altair as alt
import pandas as pd
import streamlit as st

from app.comum import milhar

DESCRICAO = {
    "v1": "Formulação v1 · **queda de consumo**: quanto maior a queda, maior a prioridade.",
    "v2": "Formulação v2 · **queda de consumo inexplicada**: desconta imóvel vazio, troca de hidrômetro, "
          "sazonalidade e mudança de uso (`queda_explicada`).",
}


def _carregar(c, f):
    try:
        return c.arm.ler_json("experimento", f"{c.referencia}_{f}")
    except FileNotFoundError:
        return None


def render_formulacao(c, f: str) -> None:
    st.title(f"Teste A/B · PoC {f}")
    st.caption(DESCRICAO[f])
    r = _carregar(c, f)
    if not r:
        st.info(f"Resultado do teste A/B da {f} ainda não disponível para {c.referencia}.")
        return
    regra, poc, base = r["regra_antiga"], r["poc"], r["linha_de_base_taxa"]
    d = pd.DataFrame({"estratégia": ["Regra antiga", f"PoC {f}"],
                      "taxa": [regra["taxa_acerto"], poc["taxa_acerto"]],
                      "m3": [regra["volume_por_visita_m3"], poc["volume_por_visita_m3"]]})
    cor = "#2b7a78" if poc["taxa_acerto"] > regra["taxa_acerto"] else "#d1603d"
    barras = alt.Chart(d).mark_bar().encode(
        x=alt.X("estratégia", sort=None, axis=alt.Axis(labelAngle=0, title=None)),
        y=alt.Y("taxa", axis=alt.Axis(format="%", title="Taxa de acerto das visitas")),
        color=alt.Color("estratégia", legend=None, scale=alt.Scale(range=["#8a8f98", cor])))
    linha = alt.Chart(pd.DataFrame({"y": [base]})).mark_rule(strokeDash=[6, 4], color="black").encode(y="y")
    rotulo = barras.mark_text(dy=-8).encode(text=alt.Text("taxa", format=".1%"))
    st.altair_chart(barras + linha + rotulo, width="stretch")
    st.caption(f"Linha tracejada: linha de base de 1 em 5 ({base:.0%}). "
               f"{regra['visitas']} visitas por grupo, 6 equipes contra 6.")

    veredito = "vence" if r["poc_vence_regra"] else "perde para"
    (st.success if r["poc_vence_regra"] else st.error)(
        f"A PoC {f} **{veredito}** a regra antiga: {r['poc_menos_regra_pp']:+.1f} pp na taxa de acerto.")

    a, b, cc = st.columns(3)
    a.metric("Acerto · regra antiga", f"{regra['taxa_acerto']:.1%}", f"{regra['acertos']} de {regra['visitas']} visitas",
             delta_color="off")
    b.metric(f"Acerto · PoC {f}", f"{poc['taxa_acerto']:.1%}", f"{r['poc_menos_regra_pp']:+.1f} pp vs regra")
    cc.metric("m³/mês por visita (PoC)", f"{poc['volume_por_visita_m3']:.2f}",
              f"{r['delta_volume_por_visita_m3']:+.2f} vs regra")

    st.subheader("Por que as visitas não encontraram irregularidade")
    causas = pd.DataFrame({
        "causa": sorted(set(regra["sem_irregularidade_por_causa"]) | set(poc["sem_irregularidade_por_causa"]) | {"sem_acesso"}),
    })
    causas["Regra antiga"] = causas["causa"].map({**regra["sem_irregularidade_por_causa"], "sem_acesso": regra["sem_acesso"]}).fillna(0).astype(int)
    causas[f"PoC {f}"] = causas["causa"].map({**poc["sem_irregularidade_por_causa"], "sem_acesso": poc["sem_acesso"]}).fillna(0).astype(int)
    st.dataframe(causas.rename(columns={"causa": "causa"}), hide_index=True, width="stretch")

    st.subheader(f"Valor estimado da PoC {f} contra a regra")
    x, y = st.columns(2)
    x.metric("Pontos de perda aparente (1 fila mensal)", f"{r['ganho_pontos_perda_aparente_1_fila']:.3f} pp")
    y.metric("Reais por ano (1 fila mensal)", f"R$ {milhar(r['ganho_reais_ano_1_fila'])}")
    st.caption(f"Doze filas mensais: {r['ganho_pontos_perda_aparente_12_filas']:.2f} pp ≈ "
               f"R$ {milhar(r['ganho_reais_ano_12_filas'])}/ano. Estimativa, não promessa.")
