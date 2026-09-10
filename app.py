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
ACCENT = "#E8590C"  # REGRA: laranja marca data centers, e nada alem disso.
#                       Cinza e todo o resto: pais, contexto, marcacao de evento.
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
    """Milhar em pt-BR: 6422 -> 6.422"""
    return f"{int(n):,}".replace(",", ".")


def pct(x, casas=1):
    """Decimal em pt-BR: 19.9 -> 19,9"""
    return f"{x:.{casas}f}".replace(".", ",")


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
st.markdown(
    "## A evolução do consumo energético frente ao crescimento dos data centers, um comparativo entre Irlanda e Brasil"
)
st.markdown(
    f"<p style='font-size:1.25rem;margin-top:-8px;margin-bottom:32px;line-height:1.5'>"
    f"Entre 2015 e 2025, o consumo da Irlanda subiu {fmt(d_total)} GWh; "
    f"data centers responderam por <b style='color:{ACCENT}'>{fmt(d_dc)} GWh, "
    f"{pct(pct_dc, 0)}% do total</b>. Hoje, eles são 23% de toda a eletricidade medida "
    f"no país.</p>",
    unsafe_allow_html=True,
)
with st.expander("Público-alvo, demanda de informação e perguntas norteadoras"):
    st.markdown("""
**Público-alvo.** Gestor público municipal de cidade candidata a receber um
data center, com poder sobre zoneamento, incentivo fiscal e contrapartidas.

**Demanda de informação.** Entender o que a expansão de data centers fez com o
sistema elétrico de um país que passou por ela antes, e onde o Brasil está
nessa trajetória.

**Questão central.** Quanto do crescimento do consumo elétrico da Irlanda entre
2015 e 2025 foi explicado por data centers, e quanto por todo o resto do país?

**Perguntas norteadoras**

1. Quem explica o crescimento do consumo elétrico da Irlanda desde 2015?
2. Em que nível a Irlanda estava quando surgiram restrições a novas conexões,
   e quanto tempo levou para chegar lá?
3. O ritmo de crescimento mudou depois da restrição?
4. Por que o percentual trimestral não serve para acompanhar isso?
5. Onde o Brasil está nessa trajetória?
        """)

st.divider()


# ---------------------------------------------------------------------------
# BLOCO 1  -  VISAO GERAL   (chunk 1)
# ---------------------------------------------------------------------------
st.subheader("O consumo energético na Irlanda na última década")

bloco1 = st.container(border=True)
with bloco1:
    c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("**Crescimento do consumo energético de 2015 a 2025**")
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
    st.markdown(f"**Como os {fmt(d_total)} GWh de crescimento estão divididos**")
    contrib = pd.DataFrame(
        {
            "grupo": ["Data centers", "Todo o resto do país"],
            "delta": [d_dc, d_resto],
        }
    )
    contrib["rotulo"] = [
        f"{fmt(v)} GWh  ({pct(v / d_total * 100, 0)}%)" for v in contrib.delta
    ]
    g2 = (
        alt.Chart(contrib)
        .mark_bar(height=52)
        .encode(
            # sort="-x" e ignorado quando o grafico tem camadas: o Vega cai em
            # ordem alfabetica. Lista explicita e a unica forma confiavel aqui.
            y=alt.Y(
                "grupo:N",
                title=None,
                sort=alt.Sort(["Data centers", "Todo o resto do país"]),
                axis=alt.Axis(labelLimit=260, grid=False),
            ),
            x=alt.X(
                "delta:Q",
                title="Crescimento em GWh",
                axis=alt.Axis(grid=False, tickCount=4),
                # folga para o rotulo (valor + participacao) caber na area
                scale=alt.Scale(domain=[0, d_dc * 1.45]),
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
        .properties(height=280)
    )
    val = g2.mark_text(
        align="left", dx=8, fontSize=F_VALOR, fontWeight="bold", color=ACCENT
    ).encode(text="rotulo:N")
    st.altair_chart(base_eixos(g2 + val), use_container_width=True, theme=None)
    st.caption(
        f"Residências, indústria, comércio e todo o resto somados cresceram "
        f"{pct(d_resto / anual.resto.iloc[0] * 100, 0)}% em dez anos."
    )


# ---------------------------------------------------------------------------
# BLOCO 2  -  A JANELA DE DECISAO   (chunk 2)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Em 2021, o órgão regulador irlandês restringe novas conexões")

bloco2 = st.container(border=True)
with bloco2:
    c3, c4 = st.columns(2)

with c3:
    st.markdown(
        "**O consumo elétrico dos data centers, antes e depois da restrição imposta pelo regulador**"
    )
    esc = alt.Scale(domain=[2014.6, 2025.4])

    banda = (
        alt.Chart(pd.DataFrame({"x": [2015], "x2": [ANO_BLOQUEIO]}))
        .mark_rect(color=GRAY_DARK, opacity=0.07)
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
                {
                    "x": [2018],
                    "y": [anual.share.max() * 0.95],
                    "t": ["6 anos: 2015 → 2021"],
                }
            )
        )
        .mark_text(fontSize=22, fontWeight="bold", color=GRAY_DARK)
        .encode(x=alt.X("x:Q", scale=esc), y="y:Q", text="t:N")
    )
    txt2 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "x": [ANO_BLOQUEIO],
                    "y": [anual.share.max() * 0.55],
                    "t": ["Restrição a novas conexões (Grande Dublin)"],
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
        "A restrição respondeu à capacidade da rede na Grande Dublin, e nenhum "
        "percentual nacional foi usado como gatilho. Os 6 anos "
        "contam do início da série do CSO, que já pega a expansão em curso."
    )

with c4:
    st.markdown("**O ritmo de crescimento ano a ano**")
    cr = anual.dropna(subset=["cresc_dc"]).copy()
    # Antes, laranja marcava "depois de 2021" e tambem significava data centers
    # no resto do painel. Dois sentidos para a mesma cor. Agora so o ano da
    # intervencao recebe destaque; a queda depois dele fica por conta da altura.
    # Todas as barras medem a mesma coisa (crescimento dos data centers), entao
    # todas recebem laranja. O ano da restricao e marcado por regra tracejada,
    # que e "marcas adicionadas", nao por uma segunda cor.
    g4 = (
        alt.Chart(cr)
        .mark_bar(color=ACCENT)
        .encode(
            x=alt.X("ano:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("cresc_dc:Q", title="Crescimento anual dos data centers (%)"),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("cresc_dc:Q", title="Crescimento no ano (%)", format=".1f"),
            ],
        )
        .properties(height=ALTURA)
    )
    # O ano precisa ser int, igual ao do grafico. Passar "2022" como texto
    # nao casa com o dominio ordinal e o Vega joga a anotacao no inicio do eixo.
    nota4 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "ano": [ANO_BLOQUEIO],
                    "y": [cr.cresc_dc.max() * 1.04],
                    "t": ["ano da restrição"],
                }
            )
        )
        .mark_text(
            align="left", dx=6, fontSize=F_ANOTACAO, fontWeight="bold", color=GRAY_DARK
        )
        .encode(x=alt.X("ano:O"), y="y:Q", text="t:N")
    )
    regra4 = (
        alt.Chart(pd.DataFrame({"ano": [ANO_BLOQUEIO]}))
        .mark_rule(color=GRAY_DARK, strokeDash=[6, 4], strokeWidth=2)
        .encode(x=alt.X("ano:O"))
    )
    st.altair_chart(
        base_eixos(g4 + regra4 + nota4), use_container_width=True, theme=None
    )
    st.caption(
        "O crescimento caiu de 32% para 10% ao ano e seguiu positivo durante "
        "todo o período de restrição. A regulação atrasou a curva sem reverter."
    )


# ---------------------------------------------------------------------------
# BLOCO 3  -  A ARMADILHA DO DADO   (chunk 3)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("A influência das estações do ano no consumo energético da Irlanda")

bloco3 = st.container(border=True)
with bloco3:
    st.markdown(
        "**A variação do consumo geral do país e do consumo dos data centers "
        "conforme a estação**"
    )
# Rotulo legivel para o tooltip. "2015Q1" e notacao de planilha; no tooltip
# cabe o nome por extenso, que e onde o leitor busca detalhe.
MESES = {"Q1": "jan a mar", "Q2": "abr a jun", "Q3": "jul a set", "Q4": "out a dez"}
df["periodo"] = [f"{r.quarter[:4]}, {MESES[r.quarter[-2:]]}" for r in df.itertuples()]

q = df.melt(
    id_vars=["quarter", "periodo"],
    value_vars=["data_center_consumption", "total_consumption"],
    var_name="serie",
    value_name="gwh",
).replace(
    {
        "data_center_consumption": "Data centers",
        "total_consumption": "Consumo total do país",
    }
)
# Dois paineis com escala Y propria, no lugar de duas linhas na mesma escala.
# Na escala unica o laranja ficava esmagado no rodape: a legenda afirmava que ele
# sobe reto, mas o leitor nao tinha como conferir. Agora da para ver o serrilhado
# de uma curva contra a suavidade da outra.
# Eixo com o ano por extenso, sem o sufixo de trimestre: a marca continua no
# primeiro trimestre, mas o rotulo lido e so "2015", "2016"...
EIXO_Q = alt.Axis(
    labelAngle=0,
    labelFontSize=F_EIXO,
    values=[f"{a}Q1" for a in range(2015, 2026)],
    labelExpr="replace(datum.label, 'Q1', '')",
    title=None,
)

# Titulo so no painel de baixo, para nao repetir a mesma frase duas vezes.
EIXO_Q_BASE = alt.Axis(
    labelAngle=0,
    labelFontSize=F_EIXO,
    values=[f"{a}Q1" for a in range(2015, 2026)],
    labelExpr="replace(datum.label, 'Q1', '')",
    titleFontSize=13,
)

p_total = (
    alt.Chart(q[q.serie == "Consumo total do país"])
    .mark_line(
        strokeWidth=2.5,
        color=GRAY_MID,
        point=alt.OverlayMarkDef(size=24, filled=True, color=GRAY_MID),
    )
    .encode(
        x=alt.X("quarter:O", title=None, axis=EIXO_Q),
        y=alt.Y("gwh:Q", title="Consumo do país", axis=alt.Axis(tickCount=4)),
        tooltip=[
            alt.Tooltip("periodo:N", title="Período"),
            alt.Tooltip("gwh:Q", title="GWh", format=","),
        ],
    )
    .properties(height=190)
)

p_dc = (
    alt.Chart(q[q.serie == "Data centers"])
    .mark_line(
        strokeWidth=3,
        color=ACCENT,
        point=alt.OverlayMarkDef(size=24, filled=True, color=ACCENT),
    )
    .encode(
        x=alt.X("quarter:O", title=None, axis=EIXO_Q_BASE),
        y=alt.Y("gwh:Q", title="Data centers", axis=alt.Axis(tickCount=4)),
        tooltip=[
            alt.Tooltip("periodo:N", title="Período"),
            alt.Tooltip("gwh:Q", title="GWh", format=","),
        ],
    )
    .properties(height=190)
)

# Anotacoes no PRIMEIRO ciclo da serie, que e onde o olho comeca a ler, e nao
# no meio do grafico. Cada rotulo vem acompanhado de um ponto destacado: sem o
# ponto, o texto flutua e o leitor nao sabe a que ele se refere.
_marcas = pd.DataFrame(
    [
        {
            "quarter": "2015Q1",
            "gwh": int(df.loc[df.quarter == "2015Q1", "total_consumption"].iloc[0]),
            "t": "inverno",
            "dy": -18,
        },
        {
            "quarter": "2015Q3",
            "gwh": int(df.loc[df.quarter == "2015Q3", "total_consumption"].iloc[0]),
            "t": "verão",
            "dy": 22,
        },
    ]
)

pontos_marca = (
    alt.Chart(_marcas)
    .mark_point(size=140, filled=True, color=INK, opacity=1)
    .encode(x=alt.X("quarter:O"), y="gwh:Q")
)


# dy e propriedade de mark, nao canal de encoding: por isso duas marcas
# separadas, uma acima do pico e outra abaixo do vale.
def _rotulo(trimestre, deslocamento):
    return (
        alt.Chart(_marcas[_marcas.quarter == trimestre])
        .mark_text(
            align="left",
            dx=10,
            dy=deslocamento,
            fontSize=F_ANOTACAO,
            fontWeight="bold",
            color=INK,
        )
        .encode(x=alt.X("quarter:O"), y="gwh:Q", text="t:N")
    )


rotulos_marca = _rotulo("2015Q1", -18) + _rotulo("2015Q3", 22)

g5 = alt.vconcat(p_total + pontos_marca + rotulos_marca, p_dc, spacing=10)

with bloco3:
    st.altair_chart(base_eixos(g5), use_container_width=True, theme=None)
    st.caption(
        "Cada painel tem escala própria, para dar para ver o formato das duas curvas. "
        "Em cima o consumo do país sobe e desce a cada estação; embaixo os data "
        "centers sobem quase reto. O percentual trimestral vai de "
        f"{pct(df[df.ano == 2024].consumption_usage.min())}% a "
        f"{pct(df[df.ano == 2024].consumption_usage.max())}% dentro de 2024 sem que "
        "nada tenha mudado nos data centers."
    )


# ---------------------------------------------------------------------------
# BLOCO 4  -  ONDE O BRASIL ESTA   (chunk 4)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("A trajetória do Brasil")

bloco4 = st.container(border=True)
with bloco4:
    c5, c6 = st.columns([2, 3])

with c5:
    st.metric(
        "Data centers no consumo elétrico do Brasil, 2024",
        "1,7%",
        help="Fonte: Brasscom, associação das empresas de TIC. Como é "
        "parte interessada, o número aparece aqui sempre identificado. "
        "Não foi possível conferir no estudo original.",
    )
    st.markdown(
        f"<p style='font-size:1.05rem;line-height:1.5'>O Brasil está hoje "
        f"<b>abaixo do ponto onde a série irlandesa começa</b>: "
        f"{pct(anual.share.iloc[0])}% em 2015, contra 1,7% aqui. Em termos de "
        f"trajetória, é o início da curva.</p>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Fontes: Central Statistics Office, instituto oficial de estatística da "
        "Irlanda, e levantamento da Brasscom no Brasil."
    )
    st.markdown(
        f"<p style='opacity:.75;font-size:.95rem;margin-top:12px'>Cerca de 97% "
        f"dos data centers irlandeses ficam na região de Dublin, onde respondem "
        f"por volta de 50% da demanda elétrica regional.</p>",
        unsafe_allow_html=True,
    )

with c6:
    st.markdown(
        "**A evolução dos pedidos de conexão de data centers no Brasil, em comparação ao consumo energético total do país**"
    )
    # Comparacao anterior (pedidos x capacidade instalada) misturava unidades:
    # pedido de conexao e potencia na rede, capacidade instalada e carga de TI.
    # Alem disso a capacidade instalada nao tem valor consensual: as fontes
    # levantadas iam de 481 a 950 MW conforme ano e metodologia.
    # Pico do sistema e pedido de conexao sao ambos potencia na rede, em GW.
    br = pd.DataFrame(
        {
            "situacao": [
                "Pico máximo de consumo do país (fev/2025)",
                "Pedidos de conexão de data centers (nov/2025)",
            ],
            "gw": [105.0, 26.2],
        }
    )
    br["rotulo"] = [f"{pct(v)} GW" for v in br.gw]
    fatia = br.gw.iloc[1] / br.gw.iloc[0] * 100

    g6 = (
        alt.Chart(br)
        .mark_bar(height=56)
        .encode(
            y=alt.Y(
                "situacao:N",
                title=None,
                sort=alt.Sort(
                    [
                        "Pico máximo de consumo do país (fev/2025)",
                        "Pedidos de conexão de data centers (nov/2025)",
                    ]
                ),
                axis=alt.Axis(labelLimit=320, grid=False),
            ),
            x=alt.X(
                "gw:Q",
                title="GW",
                axis=alt.Axis(grid=False, tickCount=4),
                scale=alt.Scale(domain=[0, 105 * 1.18]),
            ),
            color=alt.Color(
                "situacao:N",
                scale=alt.Scale(
                    domain=[
                        "Pico máximo de consumo do país (fev/2025)",
                        "Pedidos de conexão de data centers (nov/2025)",
                    ],
                    range=[GRAY_MID, ACCENT],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("situacao:N", title=" "),
                alt.Tooltip("gw:Q", title="GW", format=","),
            ],
        )
        .properties(height=260)
    )
    lbl = g6.mark_text(align="left", dx=8, fontSize=F_VALOR, fontWeight="bold").encode(
        text="rotulo:N",
        color=alt.Color(
            "situacao:N",
            scale=alt.Scale(
                domain=[
                    "Pico máximo de consumo do país (fev/2025)",
                    "Pedidos de conexão de data centers (nov/2025)",
                ],
                range=[GRAY_DARK, ACCENT],
            ),
            legend=None,
        ),
    )
    st.altair_chart(base_eixos(g6 + lbl), use_container_width=True, theme=None)
    st.caption(
        f"Os pedidos equivalem a {pct(fatia, 0)}% do maior pico de consumo já "
        "registrado no Brasil, e a fila cresce rápido: eram 19,8 GW em "
        "setembro de 2025 e passaram a 26,2 GW em novembro, um acréscimo de "
        "6,4 GW em pouco mais de 60 dias."
    )

st.divider()
st.caption(
    "Irlanda: Central Statistics Office (série 2015 a 2025) e Commission for "
    "Regulation of Utilities. Brasil: EPE (pedidos de conexão, nov/2025) e "
    "Brasscom (participação no consumo, 2024)."
)
