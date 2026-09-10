# Dashboard — Atividade 1, Visualização de Informação

## Rodar

```bash
pip install streamlit altair pandas
streamlit run app.py
```

O CSV precisa estar na mesma pasta do `app.py`. Abre em `localhost:8501`.

Testado com streamlit 1.63 e altair 6.2. Se sua versão do Altair for a 5.x,
o código deve funcionar igual — usei só API estável entre as duas.

## Os 6 gráficos e a pergunta de cada um

| # | Bloco | Pergunta que responde |
|---|---|---|
| 1 | Visão geral | **[CENTRAL]** Quanto do crescimento elétrico da Irlanda veio de data centers vs. todo o resto? |
| 2 | Visão geral | De onde veio o crescimento, em GWh absolutos |
| 3 | Janela de decisão | Em que nível o regulador interveio e quanto tempo levou para chegar lá |
| 4 | Janela de decisão | O que aconteceu com o ritmo depois da intervenção |
| 5 | Armadilha | O consumo dos data centers oscila por estação? (não — é o denominador) |
| 6 | Brasil | Onde o Brasil está nessa curva |

Regra que trava o escopo: gráfico sem pergunta sai.

## Decisões de projeto, para a avaliação cruzada

| Decisão | Conceito do material da professora |
|---|---|
| Tooltip em todos os 6 gráficos | Mantra de Shneiderman: fecha a terceira etapa, "detalhe sob demanda" |
| Cada bloco dentro de uma caixa com borda | Fechamento e proximidade; é o layout "com chunking" do próprio material |
| Rótulo direto também no gráfico trimestral | Legenda solta obriga o olho a ir e voltar para decodificar a cor |
| Anotação "← a partir do bloqueio de 2021" dentro do gráfico | Marcas adicionadas; explica a cor sem legenda redundante |
| Folga de 18% no domínio do eixo de valor | O rótulo do maior valor precisa caber dentro da área do gráfico |
| Uma cor saturada (laranja) só no que responde à pergunta daquele gráfico, resto em cinza | Pré-atentivo: matiz e intensidade |
| 4 blocos com subtítulo em vez de 6 gráficos soltos | Chunking / memória de curto prazo (4–5 itens) |
| Rótulo direto na ponta da linha em vez de legenda | Continuidade; evita ida e volta do olhar |
| Marca vertical tracejada em 2021 + banda sombreada | Marcas adicionadas e enclausuramento |
| Barras ordenadas por valor | Pregnância |
| Blocos: visão geral → zoom → detalhe → Brasil | Mantra de Shneiderman |
| Grade horizontal leve nos gráficos de linha, nenhuma nas barras | Figura/fundo; nas barras o valor já vem rotulado, grade seria ruído |
| Moldura removida, eixos em cinza claro | Figura/fundo |
| Fonte de eixo em 15px e valores em 17px, calibrados para projeção | Percepção antes de compreensão: ilegível não é interpretável |
| Separador de milhar em pt-BR (6.422, não 6,422) | Evitar interpretação equivocada |
| Frase-resposta no topo, antes de qualquer gráfico | Texto não é pré-atentivo; a hierarquia vem de cor, tamanho e posição |
| Percentual em base anual, absolutos em base trimestral | Evitar interpretação equivocada (sazonalidade do denominador) |

Laranja contra cinza é seguro para os tipos comuns de daltonismo.

## Números verificados (08/09)

| Dado | Situação | Fonte |
|---|---|---|
| 26,2 GW em pedidos de conexão | **Confirmado.** Passou de 19,8 GW (set/2025) para 26,2 GW (nov/2025) | Site da EPE |
| Pico máximo do país: 105 GW | **Confirmado**, fev/2025 | EPE, via Caderno de Transmissão do PDE 2035 |
| Fim da moratória de Dublin | **Confirmado.** Encerrada em dez/2025 por decisão da CRU, com exigência de geração própria e 80% de renovável em seis anos | CRU |
| 97% dos data centers irlandeses na região de Dublin, ~50% da demanda regional | Encontrado em análise da decisão da CRU. Usar como frase, não como gráfico | análise secundária |
| 1,7% do consumo brasileiro | **Não confirmado no estudo original.** Fica identificado no painel como levantamento da Brasscom, que é parte interessada | Brasscom |
| ~800 MW de capacidade instalada | **Descartado.** As fontes iam de 481 a 950 MW conforme ano e metodologia, e a unidade não era comparável a pedido de conexão | várias |

### Por que o gráfico 6 mudou

A versão anterior comparava 26.200 MW de pedidos de conexão com 800 MW de
capacidade instalada. São unidades diferentes: pedido de conexão é potência
contratada na rede, capacidade instalada é carga de TI, e refrigeração acrescenta
por volta de 30% sobre essa carga. O multiplicador ficava inflado por um fator
desconhecido.

A comparação atual, 26,2 GW de pedidos contra 105 GW de pico do sistema, usa a
mesma grandeza nos dois lados e vem da mesma fonte.


## O que ainda não está feito

- Ajuste fino de espaçamento e tamanho de fonte
- O texto do bloco 4 pode ganhar o contraponto do Idec (encargo sobre data centers),
  para plotar a disputa em vez de só o número da Brasscom
- Ensaio dos 10 minutos


## Tema claro é obrigatório

O `.streamlit/config.toml` força fundo claro. A hierarquia de cinzas foi calibrada
para fundo branco: em modo escuro os cinzas de contexto perdem contraste e a lógica
figura/fundo inverte.

Se o app abrir escuro, o `.streamlit/config.toml` não está na pasta de onde você
rodou o `streamlit run`. Solução imediata: menu **⋮ → Settings → Theme → Light**.
Solução definitiva: garantir que a pasta `.streamlit` esteja junto do `app.py`.


## Testar antes de subir

```bash
python teste_app.py
```

Executa o `app.py` com um Streamlit falso e valida os 6 gráficos. Serve porque
`streamlit run` subindo e a página abrindo **não** provam que o script rodou: o
Streamlit serve o HTML primeiro e executa o script depois, por websocket. Um erro
de schema do Altair só aparece na tela do navegador.

Rode este teste sempre que mexer nos gráficos, e antes de qualquer `git push`.
Saída esperada: `OK - 6 graficos construidos e validados`.


## Duas armadilhas do Altair que já custaram caro aqui

**1. `.configure()` substitui o config inteiro, não mescla.**
Internamente ele faz `copy.config = Config(**kwargs)`. Se você chamar
`.configure(locale=...)` depois de `.configure_axis(...)`, perde a configuração de
eixo inteira, silenciosamente — o gráfico continua renderizando, só que sem o que
você configurou. Por isso, em `base_eixos()`, o `.configure()` vem **primeiro**.

**2. `st.altair_chart` aplica o tema do Streamlit por padrão.**
O parâmetro é `theme="streamlit"`. Ele sobrescreve parte do seu config. Todas as
chamadas aqui passam `theme=None` para que o config do gráfico prevaleça.

Se mexer nos gráficos, rode `python teste_app.py` e confira o spec, não só a tela.
Nos dois casos acima o app sobe normalmente e o erro só aparece visualmente.


## A regra da cor, para defender na avaliação cruzada

Laranja **não** significa "data centers". Significa **"é aqui que está a resposta
da pergunta deste gráfico"**. Cinza é contexto.

Por isso, no gráfico 4, laranja marca o período pós-2021, e no gráfico 6 marca os
pedidos de conexão — não os data centers. Se alguém apontar isso como
inconsistência, a regra é essa e ela é consistente: uma cor saturada por gráfico,
sempre na resposta.

Sem essa regra explícita, a escolha parece aleatória. Com ela, cada gráfico tem
exatamente um ponto de entrada visual.