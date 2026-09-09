"""
Atividade 1 - Visualizacao de Informacao
Dashboard: expansao de data centers e consumo eletrico

Rodar:  streamlit run app.py
Dados:  electricity_data_center_consumption.csv (CSO Irlanda, 2015Q1-2025Q4)
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# PALETA  -  a decisao de design de maior retorno
# UMA cor saturada, usada SO no que responde a questao central. Resto em cinza.
# Laranja vs cinza e seguro para os tipos comuns de daltonismo.
# ---------------------------------------------------------------------------
ACCENT = "#E8590C"  # data centers  (o sujeito da questao central)
ACCENT_SOFT = "#FD9A63"  # data centers, papel secundario
GRAY_DARK = "#6C757D"  # series de contexto
GRAY_MID = "#ADB5BD"  # series de contexto, menos importante
GRAY_LINE = "#CED4DA"  # eixos e grades
INK = "#212529"  # texto

# Tamanhos calibrados para projeção em sala, não para leitura de perto.
F_EIXO = 15  # rótulos de eixo
F_TITULO_EIXO = 15  # títulos de eixo
F_VALOR = 17  # números sobre as barras
F_ROTULO = 17  # rótulo direto na ponta da linha
F_ANOTACAO = 14  # anotações dentro do gráfico
ALTURA = 400
FONTE = "Source Sans Pro, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"

# Separador de milhar em pt-BR: "6.422", não "6,422".
# "6,422" é lido como seis vírgula quatro por um leitor brasileiro.
# "currency" e obrigatorio no locale do d3 mesmo sem uso de moeda.
LOCALE_BR = {
    "number": {"decimal": ",", "thousands": ".", "grouping": [3], "currency": ["", ""]}
}


def fmt(n):
    return f"{int(n):,}".replace(",", ".")


st.set_page_config(page_title="Data centers e consumo eletrico", layout="wide")

# Fonte base maior: o dashboard e lido projetado, nao a 40cm da tela.
st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-size: 17px; }
      h2 { font-size: 2.1rem !important; line-height: 1.2; }
      h3 { font-size: 1.5rem !important; }
      .stCaption, [data-testid="stCaptionContainer"] p { font-size: 0.95rem !important; }
      [data-testid="stMetricValue"] { font-size: 2.6rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# DADOS
# ---------------------------------------------------------------------------
@st.cache_data
def carregar(caminho=None):
    caminho = caminho or BASE_DIR / "electricity_data_center_consumption.csv"
    df = pd.read_csv(caminho)
    df["ano"] = df["quarter"].str[:4].astype(int)
    df["tri"] = df["quarter"].str[-2:]
    df["resto"] = df["total_consumption"] - df["data_center_consumption"]
    return df


def agregar_anual(df):
    a = df.groupby("ano", as_index=False).agg(
        dc=("data_center_consumption", "sum"),
        total=("total_consumption", "sum"),
        resto=("resto", "sum"),
    )
    a["share"] = (a.dc / a.total * 100).round(1)
    a["cresc_dc"] = (a.dc.pct_change() * 100).round(1)
    return a


df = carregar()
anual = agregar_anual(df)

# numeros da questao central
d_dc = int(anual.dc.iloc[-1] - anual.dc.iloc[0])
d_resto = int(anual.resto.iloc[-1] - anual.resto.iloc[0])
d_total = d_dc + d_resto
pct_dc = d_dc / d_total * 100

ANO_BLOQUEIO = 2021  # moratoria de fato para novas conexoes na Grande Dublin


def base_eixos(chart):
    """Configuracao unica: sem grade vertical, sem moldura, eixo discreto."""
    # ATENCAO: .configure() SUBSTITUI o config inteiro (nao mescla).
    # Por isso ele vem primeiro; os configure_* seguintes acrescentam em cima.
    return (
        chart.configure(locale=LOCALE_BR, font=FONTE)
        .configure_view(stroke=None)
        .configure_axis(
            domainColor=GRAY_LINE,
            tickColor=GRAY_LINE,
            labelColor=GRAY_DARK,
            titleColor=GRAY_DARK,
            labelFontSize=F_EIXO,
            titleFontSize=F_TITULO_EIXO,
            grid=False,
        )
        # Grade horizontal leve so onde ajuda a ler valor (graficos de linha).
        # Nas barras o valor ja vem rotulado, entao grade seria ruido.
        .configure_axisY(grid=True, gridColor=GRAY_LINE, gridOpacity=0.45)
    )


# ---------------------------------------------------------------------------
# CABECALHO  -  a questao central antes de qualquer grafico
# ---------------------------------------------------------------------------
# Sem cor de texto fixa: quem define e o tema. So o destaque laranja e fixo,
# porque laranja tem contraste suficiente em fundo claro e escuro.
st.markdown("## Quase todo o crescimento elétrico da Irlanda veio de data centers")
st.markdown(
    f"<p style='font-size:1.25rem;margin-top:-8px;line-height:1.5'>"
    f"Entre 2015 e 2025 o consumo do país subiu {fmt(d_total)} GWh. "
    f"Data centers responderam por <b style='color:{ACCENT}'>{fmt(d_dc)} GWh, "
    f"{pct_dc:.0f}% do total</b>. Hoje eles são 23% de toda a eletricidade medida "
    f"na Irlanda.</p>"
    f"<p style='opacity:.7;font-size:.95rem;margin-top:2px'>"
    f"Feito para gestores públicos municipais avaliando a instalação de um data "
    f"center na sua cidade.</p>",
    unsafe_allow_html=True,
)
st.divider()


# ---------------------------------------------------------------------------
# BLOCO 1  -  VISAO GERAL   (chunk 1)
# ---------------------------------------------------------------------------
st.subheader("1. A Irlanda em dez anos")

bloco1 = st.container(border=True)
with bloco1:
    c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("**Quanto cada parte cresceu, ano a ano, desde 2015?**")
    # Crescimento ACUMULADO desde 2015, nao o nivel absoluto.
    # Duas series partindo de zero podem ter a inclinacao comparada direto.
    # No grafico de niveis, o cinza em 24.000 e o laranja em 1.200 estavam em
    # escalas tao diferentes que a leitura imediata era o oposto da mensagem.
    base = anual.iloc[0]
    acum = pd.DataFrame(
        {
            "ano": anual.ano,
            "Data centers": anual.dc - base.dc,
            "Todo o resto do país": anual.resto - base.resto,
        }
    ).melt(id_vars="ano", var_name="grupo", value_name="gwh")

    g1 = (
        alt.Chart(acum)
        .mark_line(strokeWidth=4)
        .encode(
            x=alt.X("ano:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "gwh:Q",
                title="Crescimento acumulado desde 2015 (GWh)",
                axis=alt.Axis(tickCount=6),
            ),
            color=alt.Color(
                "grupo:N",
                scale=alt.Scale(
                    domain=["Data centers", "Todo o resto do país"],
                    range=[ACCENT, GRAY_MID],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("grupo:N", title=" "),
                alt.Tooltip("gwh:Q", title="Crescimento acumulado (GWh)", format=","),
            ],
        )
        .properties(height=ALTURA)
    )

    # rotulo direto na ponta, no lugar de legenda
    ult = acum[acum.ano == acum.ano.max()].copy()
    ult["txt"] = ult.grupo + "   +" + ult.gwh.map(fmt)
    rot = (
        alt.Chart(ult)
        .mark_text(align="right", dx=-10, dy=-16, fontSize=F_ROTULO, fontWeight="bold")
        .encode(
            x=alt.X("ano:O"),
            y="gwh:Q",
            text="txt:N",
            color=alt.Color(
                "grupo:N",
                scale=alt.Scale(
                    domain=["Data centers", "Todo o resto do país"],
                    range=[ACCENT, GRAY_DARK],
                ),
                legend=None,
            ),
        )
    )

    st.altair_chart(base_eixos(g1 + rot), use_container_width=True, theme=None)
    st.caption(
        "As duas partem de zero em 2015, então a inclinação pode ser comparada "
        "direto. Fonte: CSO Irlanda, Data Centres Metered Electricity Consumption."
    )

with c2:
    st.markdown("**O crescimento de 2015 a 2025, repartido**")
    contrib = pd.DataFrame(
        {
            "grupo": ["Data centers", "Todo o resto do país"],
            "delta": [d_dc, d_resto],
        }
    )
    contrib["rotulo"] = contrib.delta.map(fmt)
    g2 = (
        alt.Chart(contrib)
        .mark_bar(height=52)
        .encode(
            y=alt.Y(
                "grupo:N",
                title=None,
                sort="-x",
                axis=alt.Axis(labelLimit=260, grid=False),
            ),
            x=alt.X(
                "delta:Q",
                title="Crescimento em GWh",
                axis=alt.Axis(grid=False, tickCount=4),
                # folga de 18% para o rotulo do valor caber dentro da area
                scale=alt.Scale(domain=[0, d_dc * 1.18]),
            ),
            color=alt.Color(
                "grupo:N",
                scale=alt.Scale(
                    domain=["Data centers", "Todo o resto do país"],
                    range=[ACCENT, GRAY_MID],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("grupo:N", title=" "),
                alt.Tooltip("delta:Q", title="Crescimento (GWh)", format=","),
            ],
        )
        .properties(height=ALTURA)
    )
    val = g2.mark_text(
        align="left", dx=8, fontSize=F_VALOR, fontWeight="bold", color=ACCENT
    ).encode(text="rotulo:N")
    st.altair_chart(base_eixos(g2 + val), use_container_width=True, theme=None)
    st.caption(
        f"Residências, indústria, comércio e todo o resto somados cresceram "
        f"{d_resto / anual.resto.iloc[0] * 100:.0f}% em dez anos."
    )


# ---------------------------------------------------------------------------
# BLOCO 2  -  A JANELA DE DECISAO   (chunk 2)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("2. Quanto tempo passou até a rede travar")

bloco2 = st.container(border=True)
with bloco2:
    c3, c4 = st.columns(2)

with c3:
    st.markdown(
        "**Em que nível a Irlanda estava quando o regulador bloqueou "
        "novas conexões, e quanto tempo levou para chegar lá?**"
    )
    esc = alt.Scale(domain=[2014.6, 2025.4])

    banda = (
        alt.Chart(pd.DataFrame({"x": [2015], "x2": [ANO_BLOQUEIO]}))
        .mark_rect(color=ACCENT, opacity=0.08)
        .encode(x=alt.X("x:Q", scale=esc), x2="x2:Q")
    )
    linha = (
        alt.Chart(anual)
        .mark_line(strokeWidth=3.5, color=ACCENT)
        .encode(
            x=alt.X(
                "ano:Q",
                title=None,
                scale=esc,
                axis=alt.Axis(format="d", values=list(range(2015, 2026, 2))),
            ),
            y=alt.Y("share:Q", title="% do consumo elétrico medido"),
            tooltip=[
                alt.Tooltip("ano:Q", title="Ano", format="d"),
                alt.Tooltip("share:Q", title="% do consumo", format=".1f"),
            ],
        )
    )
    marca = (
        alt.Chart(pd.DataFrame({"x": [ANO_BLOQUEIO]}))
        .mark_rule(color=GRAY_DARK, strokeDash=[6, 4])
        .encode(x=alt.X("x:Q", scale=esc))
    )
    txt = (
        alt.Chart(
            pd.DataFrame(
                {"x": [2018], "y": [anual.share.max() * 0.95], "t": ["6 anos"]}
            )
        )
        .mark_text(fontSize=22, fontWeight="bold", color=ACCENT)
        .encode(x=alt.X("x:Q", scale=esc), y="y:Q", text="t:N")
    )
    txt2 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "x": [ANO_BLOQUEIO],
                    "y": [anual.share.max() * 0.55],
                    "t": ["Bloqueio de novas conexões (Dublin)"],
                }
            )
        )
        .mark_text(fontSize=F_ANOTACAO, align="left", dx=8, color=GRAY_DARK)
        .encode(x=alt.X("x:Q", scale=esc), y="y:Q", text="t:N")
    )
    st.altair_chart(
        base_eixos(banda + linha + marca + txt + txt2),
        use_container_width=True,
        theme=None,
    )
    st.caption(
        "Duas ressalvas. O bloqueio respondeu à capacidade da rede na Grande "
        "Dublin; nenhum percentual nacional foi usado como gatilho. E os 6 anos "
        "contam do início da série do CSO, que já pega a expansão em curso."
    )

with c4:
    st.markdown("**O ritmo de crescimento ano a ano**")
    cr = anual.dropna(subset=["cresc_dc"]).copy()
    cr["fase"] = (cr.ano >= ANO_BLOQUEIO).map(
        {True: "Depois de 2021", False: "Antes de 2021"}
    )
    g4 = (
        alt.Chart(cr)
        .mark_bar()
        .encode(
            x=alt.X("ano:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("cresc_dc:Q", title="Crescimento anual dos data centers (%)"),
            color=alt.Color(
                "fase:N",
                scale=alt.Scale(
                    domain=["Antes de 2021", "Depois de 2021"], range=[GRAY_MID, ACCENT]
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("cresc_dc:Q", title="Crescimento no ano (%)", format=".1f"),
            ],
        )
        .properties(height=ALTURA)
    )
    nota4 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "ano": ["2022"],
                    "y": [cr.cresc_dc.max() * 1.02],
                    "t": ["← a partir do bloqueio de 2021"],
                }
            )
        )
        .mark_text(
            align="left", dx=4, fontSize=F_ANOTACAO, fontWeight="bold", color=ACCENT
        )
        .encode(x=alt.X("ano:O"), y="y:Q", text="t:N")
    )
    st.altair_chart(base_eixos(g4 + nota4), use_container_width=True, theme=None)
    st.caption(
        "O crescimento caiu de 32% para 10% ao ano, e seguiu positivo mesmo sob "
        "moratória. A regulação atrasou a curva sem reverter. Vale ler como "
        "coincidência no tempo: saturação de mercado e limite de rede explicariam "
        "o mesmo padrão. [VERIFICAR status atual da moratória na CRU/EirGrid]"
    )


# ---------------------------------------------------------------------------
# BLOCO 3  -  A ARMADILHA DO DADO   (chunk 3)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("3. Por que não usamos o percentual trimestral")

bloco3 = st.container(border=True)
with bloco3:
    st.markdown(
        "**O consumo dos data centers varia conforme a estação do ano?**  "
        "Quem varia é o consumo do país, que entra como denominador."
    )
q = df.melt(
    id_vars="quarter",
    value_vars=["data_center_consumption", "total_consumption"],
    var_name="serie",
    value_name="gwh",
).replace(
    {
        "data_center_consumption": "Data centers",
        "total_consumption": "Consumo total do país",
    }
)
g5 = (
    alt.Chart(q)
    .mark_line(strokeWidth=2.5)
    .encode(
        x=alt.X(
            "quarter:O",
            title=None,
            axis=alt.Axis(
                labelAngle=0,
                labelFontSize=F_EIXO,
                values=[f"{a}Q1" for a in range(2015, 2026)],
            ),
        ),
        y=alt.Y("gwh:Q", title="GWh no trimestre"),
        color=alt.Color(
            "serie:N",
            scale=alt.Scale(
                domain=["Data centers", "Consumo total do país"],
                range=[ACCENT, GRAY_MID],
            ),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("quarter:O", title="Trimestre"),
            alt.Tooltip("serie:N", title=" "),
            alt.Tooltip("gwh:Q", title="GWh", format=","),
        ],
    )
    .properties(height=ALTURA)
)
# Rotulo direto em vez de legenda: o material critica legenda solta,
# porque obriga o olho a ir e voltar para decodificar a cor.
ult_q = q[q.quarter == q.quarter.max()]
rot5 = (
    alt.Chart(ult_q)
    .mark_text(align="right", dx=-6, dy=-16, fontSize=F_ROTULO, fontWeight="bold")
    .encode(
        x=alt.X("quarter:O"),
        y="gwh:Q",
        text="serie:N",
        color=alt.Color(
            "serie:N",
            scale=alt.Scale(
                domain=["Data centers", "Consumo total do país"],
                range=[ACCENT, GRAY_DARK],
            ),
            legend=None,
        ),
    )
)
with bloco3:
    st.altair_chart(base_eixos(g5 + rot5), use_container_width=True, theme=None)
    st.caption(
        "A linha cinza sobe e desce com aquecimento e iluminação. A laranja sobe "
        "quase reto. O resultado é que o percentual trimestral vai de "
        f"{df[df.ano == 2024].consumption_usage.min():.1f}% a "
        f"{df[df.ano == 2024].consumption_usage.max():.1f}% dentro de 2024 sem que "
        "nada tenha mudado nos data centers. Por isso o percentual aparece aqui "
        "sempre em base anual."
    )


# ---------------------------------------------------------------------------
# BLOCO 4  -  ONDE O BRASIL ESTA   (chunk 4)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("4. O Brasil na mesma curva")

bloco4 = st.container(border=True)
with bloco4:
    c5, c6 = st.columns([2, 3])

with c5:
    st.metric(
        "Data centers no consumo elétrico do Brasil, 2024",
        "1,7%",
        help="Fonte: Brasscom, associação das empresas do setor. "
        "[VERIFICAR no estudo original]",
    )
    st.markdown(
        f"<p style='opacity:.75;font-size:1rem'>É menos que o ponto de partida "
        f"da série irlandesa, que abre em {anual.share.iloc[0]:.1f}% no ano de "
        f"2015. A comparação tem limite: o dado irlandês vem do instituto oficial "
        f"de estatística e o brasileiro, de um levantamento da associação das "
        f"empresas do setor.</p>",
        unsafe_allow_html=True,
    )

with c6:
    st.markdown("**Pedidos de conexão e capacidade instalada, em MW**")
    br = pd.DataFrame(
        {
            "situacao": ["Pedidos de conexão à rede", "Capacidade já instalada"],
            "mw": [
                26200,
                800,
            ],  # [VERIFICAR] EPE, nov/2025 - Caderno de Transmissao PDE 2035
        }
    )
    br["rotulo"] = br.mw.map(fmt)
    g6 = (
        alt.Chart(br)
        .mark_bar(height=56)
        .encode(
            y=alt.Y(
                "situacao:N",
                title=None,
                sort="-x",
                axis=alt.Axis(labelLimit=260, grid=False),
            ),
            x=alt.X(
                "mw:Q",
                title="MW",
                axis=alt.Axis(grid=False, tickCount=4),
                scale=alt.Scale(domain=[0, 26200 * 1.18]),
            ),
            color=alt.Color(
                "situacao:N",
                scale=alt.Scale(
                    domain=["Pedidos de conexão à rede", "Capacidade já instalada"],
                    range=[ACCENT, GRAY_MID],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("situacao:N", title=" "),
                alt.Tooltip("mw:Q", title="MW", format=","),
            ],
        )
        .properties(height=260)
    )
    lbl = g6.mark_text(
        align="left", dx=8, fontSize=F_VALOR, fontWeight="bold", color=ACCENT
    ).encode(text="rotulo:N")
    st.altair_chart(base_eixos(g6 + lbl), use_container_width=True, theme=None)
    st.caption(
        "Fonte: EPE, nov/2025. [VERIFICAR no Caderno de Transmissão do PDE 2035]"
    )

st.divider()
st.caption(
    "Irlanda: Central Statistics Office. Brasil: EPE e Brasscom. "
    "Série de 2015 a 2025 para a Irlanda; dado brasileiro de 2024 e 2025."
)
