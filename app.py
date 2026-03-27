import streamlit as st
import plotly.express as px
import pandas as pd
import base64
from PIL import Image
import io
import plotly.colors as colors
from matplotlib import colors as mcolors
import numpy as np

st.set_page_config(page_title="Indicadores de Mortalidade no Brasil", layout="wide")

image = Image.open("Logo uepb.png")
buffered = io.BytesIO()
image.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

st.markdown(f"""
    <style>
        .top-bar {{
            background-color: #000000;
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
        }}
        .text-content {{
            display: flex;
            flex-direction: column;
            max-width: 85%;
        }}
        .top-bar h1 {{
            margin: 0;
            font-size: 30px;  /* Aumentado */
            font-weight: bold;
        }}
        .top-bar p {{
            margin: 5px 0 0 0;
            font-size: 20px;  /* Aumentado */
        }}
        .top-bar img {{
            height: 90px;  /* Aumentado também se quiser mais destaque */
        }}
    </style>

    <div class="top-bar">
        <div class="text-content">
            <h1>📊 Indicadores de Mortalidade Infantil e Óbitos por Causas Externas - Municípios e Regiões do Brasil</h1>
            <p>📊 Projeto desenvolvido em parceria com o Lab Multiusuário da UEPB</p>
        </div>
        <img src="data:image/png;base64,{img_base64}" alt="Logo">
    </div>
""", unsafe_allow_html=True)


df_mortalidade = pd.read_excel("Mortalidade infantil - Brasil.xlsx")
df_obitos = pd.read_excel("Óbitos por Causas Externas - Brasil.xlsx")
df_taxa_obitos = pd.read_excel("TAXA DOS OBITOS POR CAUSAS EXTERNAS - REGIÃO.xlsx")
df_taxa_mortalidade = pd.read_excel("TAXA DA MORTALIDADE INFANTIL - REGIÃO.xlsx")

filtro_municipio = st.text_input("🔎 Filtrar por Município (nome completo ou parte dele)")

dark_style = """
    <style>
    .stApp { background-color: #1a2c5b; }
    .stButton>button { border-radius: 5px; padding: 0.5em 1em; font-weight: bold; }
    .stTabs [role="tablist"] > div:hover {
        background-color: #2b3f75; transform: scale(1.05); cursor: pointer;
    }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: white; }
    </style>
"""
st.markdown(dark_style, unsafe_allow_html=True)

def plot_violino_histograma_multicol(df, anos, titulo_base):
    for i in range(0, len(anos), 2):
        cols = st.columns(4)
        for j in range(2):
            if i + j < len(anos):
                ano = anos[i + j]
                with cols[j*2]:
                    fig_hist = px.histogram(df, x=ano, nbins=20,
                                            title=f"Histograma - {ano}", color_discrete_sequence=["#1a2c5b"])
                    st.plotly_chart(fig_hist, use_container_width=True)
                with cols[j*2 + 1]:
                    fig_violin = px.violin(df, y=ano, box=True, points="all",
                                           title=f"Gráfico de Violino - {ano}", color_discrete_sequence=["#1a2c5b"])
                    st.plotly_chart(fig_violin, use_container_width=True)

def plot_serie_temporal(df, anos, titulo):
    df_total = df[anos].sum().reset_index()
    df_total.columns = ["Ano", "Total"]
    fig = px.line(df_total, x="Ano", y="Total", markers=True, title=f"Série Temporal - {titulo}", line_shape="linear")
    st.plotly_chart(fig, use_container_width=True)

def plot_comparativo(df, anos, titulo):
    df_melt = df[anos].melt(var_name="Ano", value_name="Valor")
    anos_ordenados = sorted(df_melt['Ano'].unique())

    def interpolate_colors(c1, c2, n):
        c1 = np.array(mcolors.to_rgb(c1))
        c2 = np.array(mcolors.to_rgb(c2))
        colors = [mcolors.to_hex(c1 + (c2 - c1) * i/(n-1)) for i in range(n)]
        return colors

    paleta = interpolate_colors('#FFA500', '#FF0000', len(anos_ordenados))
  #### Se preferir gráfico de violino só colocar px.violin
    fig = px.box(
        df_melt,
        x="Ano",
        y="Valor",
        color="Ano",
        color_discrete_sequence=paleta,
        title=f"Gráfico Comparativo de Boxplot - {titulo}",
        points="all"
    )
    st.plotly_chart(fig, use_container_width=True)


def aplicar_filtro(df):
    if filtro_municipio and "Município" in df.columns:
        return df[df["Município"].str.contains(filtro_municipio, case=False, na=False)]
    return df


df_mortalidade = aplicar_filtro(df_mortalidade)
df_obitos = aplicar_filtro(df_obitos)
df_taxa_mortalidade = aplicar_filtro(df_taxa_mortalidade)
df_taxa_obitos = aplicar_filtro(df_taxa_obitos)

anos_mortalidade = list(range(2013, 2024))
anos_obitos = list(range(2013, 2024))

anos_taxa_mortalidade = [col for col in df_taxa_mortalidade.columns if isinstance(col, int)]
anos_taxa_obitos = [col for col in df_taxa_obitos.columns if isinstance(col, int)]

# Abas
abas = [
    "Documentação", "Metodologia", "Ferramentas", "Resultados",
    "Mortalidade Infantil", "Óbitos Causas Externas",
    "Séries Temporais", "Gráficos Comparativos com valor absoluto", "Comparativos das Regiões - valor absoluto e taxa",
    "Verificação de tendências", "Correlações e Gráficos por Região - valor absoluto",
    "Análises da Taxa Mortalidade Infantil", "Análises da Taxa de Óbitos Causas Externas", "Referências"
]

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab_regiao, tab8, tab9, tab_taxa_mort, tab_taxa_obito, tab_ref = st.tabs(abas)

with tab0:
    st.subheader("\U0001F5C2\ufe0f Documentação da Análise")
    st.markdown("""
O presente estudo tem como foco a análise de 4 bases de dados relacionadas à saúde pública nos municípios brasileiros e nas suas 5 regiões. Sendo as 4 bases descritas a seguir

- Mortalidade Infantil com intervalo de (2013–2023)

- Óbitos por Causas Externas com intervalo de (1996–2023)

- Taxa da Mortalidade Infantil com intervalo de (1996–2023)

- Taxa de Óbitos por Causas Externas com intervalo de (1996–2023)

O principal objetivo é compreender a distribuição, a evolução temporal e os possíveis padrões dessas duas variáveis ao longo dos anos, e com isso poder identificar possíveis tendências relevantes entre os municípios do Brasil, e regiões do Brasil.

As bases "Mortalidade Infantil com intervalo de (2013–2023)" e "Óbitos por Causas Externas com intervalo de (1996–2023)" apresentavam valores faltantes (missing data / NA). Para garantir a consistência e qualidade da análise, foi realizado um tratamento prévio dos dados. A imputação dos valores ausentes foi feita com base na média anual de cada variável, preservando a coerência estatística dentro de cada ano analisado. Esse procedimento foi executado utilizando o python.

Após o tratamento, os dados foram integrados a uma aplicação interativa desenvolvida atráves do Google Colab utilizando a biblioteca Streamlit, permitindo ao usuário final explorar os resultados por meio de gráficos dinâmicos e ferramentas de visualização intuitivas e interativas.
    """)

with tab1:
    st.subheader("Metodologia")
    st.markdown("""
A metodologia adotada neste estudo pode ser resumida nas seguintes etapas:

1- Tratamento dos Dados:

- Identificação de valores ausentes em ambas as bases.
- Imputação dos dados faltantes por meio da média anual correspondente de cada variável.

2 - Análise Exploratória:

- Geração de histogramas para todos os anos das duas bases, visando observar a distribuição das variáveis.
- Elaboração de boxplots e gráficos de violino, para avaliar a variação e dispersão dos dados ao longo do tempo.

3 - Análise Comparativa:

- Comparação direta entre os dados de mortalidade infantil e óbitos por causas externas, destacando semelhanças e diferenças nas distribuições temporais.

4 - Séries Temporais:

- Construção de séries temporais para observar a tendência de crescimento ou redução das médias anuais por município e em nível nacional.

5 - Visualização Interativa:

- Implementação de botões interativos no app, permitindo ao usuário verificar se a média e as taxas está em tendência de alta, queda ou estabilidade.

6 - Análises utilizando as taxas

- Afim de evitar interpretações usando apenas números absolutos. Com isso usando taxas permite análises melhores, principalmente em estudos populacionais e epidemiológicos
    """)

with tab2:
    st.subheader("Ferramentas Utilizadas")
    st.markdown("""
As ferramentas utilizadas para o desenvolvimento da análise e visualização dos dados foram:

1- python:

Usado para tratamento inicial das bases de dados e imputação de valores faltantes por média anual.

2 -Google Colab:

Ambiente de desenvolvimento Python para análise e visualização de dados.

2 - Streamlit:

Utilizado para criar a aplicação web interativa que apresenta os gráficos, séries temporais e comparações.

Bibliotecas Python (implícitas no Colab/Streamlit):

**pandas** para manipulação de dados
**matplotlib** e seaborn para gráficos estáticos
**plotly** para visualizações interativas
**numpy** para cálculos estatísticos
 """)

with tab3:
    st.subheader("Resultados")
    st.markdown("""
Os principais resultados obtidos por meio da análise foram:

1 -Distribuição dos Dados:

- Os histogramas revelaram a variação da frequência de mortalidade infantil e óbitos por causas externas ao longo dos anos.
- Os gráficos de violino e boxplots mostraram a dispersão dos dados, destacando anos com maior desigualdade entre municípios.

2 - Tendências Temporais:

- As séries temporais demonstraram, em alguns casos, uma redução nos índices de mortalidade infantil, enquanto os óbitos por causas externas apresentaram variações regionais significativas.

3 - Comparação entre Bases:

- O estudo comparativo indicou que, apesar de distintos, os dois indicadores podem apresentar comportamentos semelhantes em determinadas regiões e períodos, apontando possíveis relações com fatores socioeconômicos.

4 -Interatividade no App:

- A aplicação permite ao usuário explorar os dados ano a ano, visualizar gráficos interativos e observar de forma clara se os indicadores estão aumentando, diminuindo ou permanecendo estáveis ao longo do tempo.
- Verificação da correlação entre os anos das bases de dados de obitos e mortalidade.

""")

with tab4:
    st.subheader("\U0001F4CA Mortalidade Infantil - Análise por Ano - Valores absolutos")
    if df_mortalidade is not None:
        plot_violino_histograma_multicol(df_mortalidade, anos_mortalidade, "Mortalidade Infantil")
    else:
        st.warning("Carregue a base de Mortalidade Infantil.")

with tab5:
    st.subheader("\U0001F4CA Óbitos por Causas Externas - Análise por Ano - Valores absolutos")
    if df_obitos is not None:
        plot_violino_histograma_multicol(df_obitos, anos_obitos, "Óbitos por Causas Externas")
    else:
        st.warning("Carregue a base de Óbitos por Causas Externas.")

with tab6:
    st.subheader("\U0001F4C8 Séries Temporais - por ano - mortalidade infantil e óbitos por causas externas - Valores absolutos")
    col1, col2 = st.columns(2)
    with col1:
        if df_mortalidade is not None:
            st.markdown("**Mortalidade Infantil**")
            plot_serie_temporal(df_mortalidade, anos_mortalidade, "Mortalidade Infantil")

    with col2:
        if df_obitos is not None:
            st.markdown("**Óbitos por Causas Externas**")
            plot_serie_temporal(df_obitos, anos_obitos, "Óbitos por Causas Externas")

with tab7:
    st.subheader("\U0001F4CA Gráficos Comparativos")

    if df_mortalidade is not None:
        st.markdown("### Mortalidade Infantil - Comparativo entre anos - valores absolutos")
        plot_comparativo(df_mortalidade, anos_mortalidade, "Mortalidade Infantil")

    if df_obitos is not None:
        st.markdown("### Óbitos por Causas Externas - Comparativo entre anos - valores absolutos")
        plot_comparativo(df_obitos, anos_obitos, "Óbitos por Causas Externas")

with tab_regiao:
    st.subheader("📍 Análise por Região")

    if df_mortalidade is not None and df_obitos is not None:
        if 'Região' in df_mortalidade.columns and 'Região' in df_obitos.columns:
            df_mort_regiao = df_mortalidade.groupby('Região')[anos_mortalidade].sum().reset_index()
            df_obito_regiao = df_obitos.groupby('Região')[anos_obitos].sum().reset_index()

            ano_selecionado = st.selectbox("Selecione o Ano para Visualizar por Região (Absoluto)", anos_mortalidade, index=len(anos_mortalidade)-1)

            col1, col2 = st.columns(2)
            with col1:
                fig_mort_regiao = px.bar(df_mort_regiao, x='Região', y=ano_selecionado,
                                         title=f"Mortalidade Infantil por Região - {ano_selecionado}",
                                         labels={ano_selecionado: 'Quantidade', 'Região': 'Região'},
                                         color='Região')
                st.plotly_chart(fig_mort_regiao, use_container_width=True)

            with col2:
                fig_obito_regiao = px.bar(df_obito_regiao, x='Região', y=ano_selecionado,
                                         title=f"Óbitos por Causas Externas por Região - {ano_selecionado}",
                                         labels={ano_selecionado: 'Quantidade', 'Região': 'Região'},
                                         color='Região')
                st.plotly_chart(fig_obito_regiao, use_container_width=True)

        else:
            st.warning("A coluna 'Região' não foi encontrada em uma ou ambas as bases de dados.")
    else:
        st.warning("Carregue ambas as bases para visualizar a análise por Região.")

    st.markdown("---")

    if df_taxa_mortalidade is not None and df_taxa_obitos is not None:
        if 'Região' in df_taxa_mortalidade.columns and 'Regiao' in df_taxa_obitos.columns:
            ano_selecionado_taxa = st.selectbox("Selecione o Ano para Visualizar por Região (Taxa)", sorted(anos_taxa_mortalidade), index=len(anos_taxa_mortalidade)-1, key="ano_taxa")

            col3, col4 = st.columns(2)
            with col3:
                fig_taxa_mort_regiao = px.bar(df_taxa_mortalidade, x='Região', y=ano_selecionado_taxa,
                                             title=f"Taxa da Mortalidade Infantil por Região - {ano_selecionado_taxa}",
                                             labels={ano_selecionado_taxa: 'Taxa', 'Região': 'Região'},
                                             color='Região')
                st.plotly_chart(fig_taxa_mort_regiao, use_container_width=True)

            with col4:
                fig_taxa_obito_regiao = px.bar(df_taxa_obitos, x='Regiao', y=ano_selecionado_taxa,
                                              title=f"Taxa de Óbitos por Causas Externas por Região - {ano_selecionado_taxa}",
                                              labels={ano_selecionado_taxa: 'Taxa', 'Regiao': 'Região'},
                                              color='Regiao')
                st.plotly_chart(fig_taxa_obito_regiao, use_container_width=True)
        else:
            st.warning("A coluna 'Região' ou 'Regiao' não foi encontrada em uma ou ambas as bases de taxas.")
    else:
        st.warning("Carregue ambas as bases de taxas para visualizar a análise por Região.")

with tab8:
    st.subheader("\U0001F4CA Análises de tendência")
    col1, col2 = st.columns(2)
    with col1:
      st.markdown("Verificação da tendência com base nas médias anuais")
      if st.button("Analisar Tendência - Mortalidade Infantil"):
        if df_mortalidade is not None:
            tendencia = df_mortalidade[anos_mortalidade].mean().diff().mean()
            if tendencia < 0:
                st.success(f"Mortalidade Infantil está em queda. Tendência média anual: {tendencia:.2f}")
            else:
                st.warning(f"Mortalidade Infantil não apresenta queda significativa. Tendência: {tendencia:.2f}")
    with col1:
      if st.button("Analisar Tendência - Óbitos por Causas Externas"):
        if df_obitos is not None:
            tendencia = df_obitos[anos_obitos].mean().diff().mean()
            if tendencia < 0:
                st.success(f"Óbitos por causas externas estão em queda. Tendência média anual: {tendencia:.2f}")
            else:
                st.warning(f"Óbitos por causas externas não apresentam queda significativa. Tendência: {tendencia:.2f}")

    with col2:
      st.markdown("Verificação da tendência com base nas taxas anuais")
      if st.button("Analisar Tendência - Taxa Mortalidade Infantil"):
        if df_taxa_mortalidade is not None:
            tendencia_taxa = df_taxa_mortalidade[anos_taxa_mortalidade].mean().diff().mean()
            if tendencia_taxa < 0:
                st.success(f"Taxa de Mortalidade Infantil está em queda. Tendência média anual: {tendencia_taxa:.2f}")
            else:
                st.warning(f"Taxa de Mortalidade Infantil não apresenta queda significativa. Tendência: {tendencia_taxa:.2f}")
    with col2:
      if st.button("Analisar Tendência - Taxa Óbitos por Causas Externas"):
        if df_taxa_obitos is not None:
            tendencia_taxa_obitos = df_taxa_obitos[anos_taxa_obitos].mean().diff().mean()
            if tendencia_taxa_obitos < 0:
                st.success(f"Taxa de Óbitos por causas externas está em queda. Tendência média anual: {tendencia_taxa_obitos:.2f}")
            else:
                st.warning(f"Taxa de Óbitos por causas externas não apresenta queda significativa. Tendência: {tendencia_taxa_obitos:.2f}")

with tab9:
    st.subheader("📊 Análise de Correlações e Distribuições por Região")
    if df_mortalidade is not None and df_obitos is not None:

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📉 Correlação - Mortalidade Infantil")
            anos_selecionados_mort = st.multiselect(
                "Selecione até 3 anos - (Mortalidade Infantil):",
                options=anos_mortalidade,
                default=anos_mortalidade[-3:],
                key="anos_corr_mort"
            )

            if len(anos_selecionados_mort) >= 2:
                corr_mort = df_mortalidade[anos_selecionados_mort].corr()
                anos_str_mort = [str(ano) for ano in anos_selecionados_mort]
                fig_corr_mort = px.imshow(
                    corr_mort, text_auto=".2f", color_continuous_scale="Blues"
                )
                st.plotly_chart(fig_corr_mort, use_container_width=True)
            else:
                st.warning("Selecione pelo menos dois anos para gerar a correlação de mortalidade infantil.")

            if 'Região' in df_mortalidade.columns:
                st.markdown("### 📉 Gráfico de setores da Mortalidade Infantil por Região (Último Ano)")
                total_mortalidade_regiao = df_mortalidade.groupby("Região")[anos_mortalidade[-1]].sum().reset_index()
                fig_pizza_mortalidade = px.pie(
                    total_mortalidade_regiao, names="Região", values=anos_mortalidade[-1],
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                st.plotly_chart(fig_pizza_mortalidade, use_container_width=True)

        with col2:
            st.markdown("### 📉 Correlação - Óbitos por Causas Externas")
            anos_selecionados_obitos = st.multiselect(
                "Selecione até 3 anos - (Óbitos por Causas Externas):",
                options=anos_obitos,
                default=anos_obitos[-3:],
                key="anos_corr_obitos"
            )

            if len(anos_selecionados_obitos) >= 2:
                corr_obito = df_obitos[anos_selecionados_obitos].corr()
                anos_str_obitos = [str(ano) for ano in anos_selecionados_obitos]
                fig_corr_obito = px.imshow(
                    corr_obito, text_auto=".2f", color_continuous_scale="Reds"
                )
                st.plotly_chart(fig_corr_obito, use_container_width=True)
            else:
                st.warning("Selecione pelo menos dois anos para gerar a correlação de óbitos.")

            if 'Região' in df_obitos.columns:
                st.markdown("### 📉 Gráfico de setores de Óbitos por Região (Último Ano)")
                total_por_regiao = df_obitos.groupby("Região")[anos_obitos[-1]].sum().reset_index()
                fig_pizza = px.pie(
                    total_por_regiao, names="Região", values=anos_obitos[-1],
                    color_discrete_sequence=px.colors.sequential.OrRd
                )
                st.plotly_chart(fig_pizza, use_container_width=True)

with tab_taxa_mort:
    if df_taxa_mortalidade is not None:
        anos_taxa_mortalidade_sorted = sorted(anos_taxa_mortalidade)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📉 Série temporal da Taxa da Mortalidade Infantil")
            medias_ano = df_taxa_mortalidade[anos_taxa_mortalidade_sorted].mean().reset_index()
            medias_ano.columns = ["Ano", "Média da Taxa"]
            fig1 = px.line(medias_ano, x="Ano", y="Média da Taxa", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("### 📉  Correlação entre Anos Selecionados")
            anos_escolhidos = st.multiselect(
                "Selecione até 3 anos:", anos_taxa_mortalidade_sorted,
                default=anos_taxa_mortalidade_sorted[:3],
                key="correlacao_taxa_mort"
            )
            if len(anos_escolhidos) == 3:
                corr_matrix = df_taxa_mortalidade[anos_escolhidos].corr()
                fig3 = px.imshow(corr_matrix, text_auto=".2f", aspect="equal",
                                 color_continuous_scale="OrRd")
                st.plotly_chart(fig3, use_container_width=True)
            elif len(anos_escolhidos) < 3:
                st.info("Selecione 3 anos para visualizar a matriz de correlação 3x3.")
            else:
                st.warning("Por favor, selecione **apenas 3 anos**.")

        with col2:
            st.markdown("#### 📉 Boxplot das Taxas de mortalidade por Ano")
            df_box = df_taxa_mortalidade[["Região"] + anos_taxa_mortalidade_sorted].melt(
                id_vars="Região", var_name="Ano", value_name="Taxa"
            )
            fig2 = px.box(df_box, x="Ano", y="Taxa", points="all", color="Ano",
                          color_discrete_sequence=px.colors.sequential.OrRd)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"### 📉  Gráfico de setores da Taxa de Mortalidade por Região ({anos_taxa_mortalidade[-1]})")
            taxa_ultimo_ano_mortalidade = anos_taxa_mortalidade[-1]
            total_taxa_mort_regiao = df_taxa_mortalidade.groupby("Região")[taxa_ultimo_ano_mortalidade].mean().reset_index()
            fig_pizza_taxa_mort = px.pie(total_taxa_mort_regiao, names="Região", values=taxa_ultimo_ano_mortalidade,
                                         color_discrete_sequence=px.colors.sequential.Reds)
            st.plotly_chart(fig_pizza_taxa_mort, use_container_width=True)

with tab_taxa_obito:
    if df_taxa_obitos is not None:
        anos_taxa_obitos_sorted = sorted(anos_taxa_obitos)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📉 Série temporal da Taxa de Óbitos por Causas Externas")
            medias_ano = df_taxa_obitos[anos_taxa_obitos_sorted].mean().reset_index()
            medias_ano.columns = ["Ano", "Média da Taxa"]
            fig1 = px.line(medias_ano, x="Ano", y="Média da Taxa", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("### 📉 Correlação entre Anos Selecionados")
            anos_escolhidos = st.multiselect(
                "Selecione até 3 anos:", anos_taxa_obitos_sorted,
                default=anos_taxa_obitos_sorted[:3],
                key="anos_obito"
            )
            if len(anos_escolhidos) == 3:
                corr_matrix = df_taxa_obitos[anos_escolhidos].corr()
                fig3 = px.imshow(corr_matrix, text_auto=".2f", aspect="equal",
                                 color_continuous_scale="OrRd")
                st.plotly_chart(fig3, use_container_width=True)
            elif len(anos_escolhidos) < 3:
                st.info("Selecione 3 anos para visualizar a matriz de correlação 3x3.")
            else:
                st.warning("Por favor, selecione **apenas 3 anos**.")

        with col2:
            st.markdown("#### 📉 Boxplot das Taxas por Ano")
            df_box = df_taxa_obitos[["Regiao"] + anos_taxa_obitos_sorted].melt(
                id_vars="Regiao", var_name="Ano", value_name="Taxa"
            )
            fig2 = px.box(df_box, x="Ano", y="Taxa", points="all", color="Ano",
                          color_discrete_sequence=px.colors.sequential.OrRd)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"#### 📉 Gráfico de setores da Taxa de óbitos por Região ({anos_taxa_obitos[-1]})")
            taxa_ultimo_ano_obitos = anos_taxa_obitos[-1]
            total_taxa_obito_regiao = df_taxa_obitos.groupby("Regiao")[taxa_ultimo_ano_obitos].mean().reset_index()
            fig_pizza_taxa_obito = px.pie(
                total_taxa_obito_regiao, names="Regiao", values=taxa_ultimo_ano_obitos,
                color_discrete_sequence=px.colors.sequential.OrRd
            )
            st.plotly_chart(fig_pizza_taxa_obito, use_container_width=True)
with tab_ref:
    st.subheader("\U0001F5C2\ufe0f Referências")
    st.markdown("""
📁 Bases de Dados Oficiais

- IBGE. Instituto Brasileiro de Geografia e Estatística. Séries Estatísticas - Mortalidade por causas externas (MS4). Disponível em: https://seriesestatisticas.ibge.gov.br/series.aspx?vcodigo=MS4. Acesso em: 15 jun. 2025.

- BRASIL. Ministério da Saúde. DATASUS. Óbitos por causas externas segundo Unidade da Federação - TABNET. Disponível em: http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sim/cnv/ext10uf.def. Acesso em: 15 jun. 2025.

- BRASIL. Ministério da Saúde. DATASUS. Indicadores de Mortalidade Infantil e Geral - TABNET IDB. Disponível em: http://tabnet.datasus.gov.br/cgi/idb2000/fqc12.htm. Acesso em: 15 jun. 2025.

- BRASIL. Ministério da Saúde. DATASUS. Indicadores Demográficos - TABNET IDB. Disponível em: http://tabnet.datasus.gov.br/cgi/idb2000/fqc01.htm. Acesso em: 15 jun. 2025.

- BRASIL. Ministério da Saúde. DATASUS. Portal de Informações de Saúde. Disponível em: https://datasus.saude.gov.br/. Acesso em: 15 jun. 2025.

- BRASIL. Ministério da Saúde. DATASUS. Acesso à Informação - DATASUS. Disponível em: https://datasus.saude.gov.br/acesso-a-informacao/. Acesso em: 15 jun. 2025.

- ALAGOAS. Secretaria de Estado da Saúde. Dados da Saúde - Portal Alagoas em Dados e Informações. Disponível em: https://dados.al.gov.br/catalogo/pt_PT/dataset/dados-da-saude/resource/04323437-19e3-4a6a-a53c-8f9102d29ff5. Acesso em: 15 jun. 2025.


🛠️ Bibliotecas e software Python

- PYTHON SOFTWARE FOUNDATION. Python: programação para todos. Disponível em: https://www.python.org/. Acesso em: 15 jun. 2025.

- STREAMLIT INC. Streamlit: The fastest way to build data apps. Disponível em: https://streamlit.io/. Acesso em: 15 jun. 2025.

- PLOTLY TECHNOLOGIES INC. Plotly Express - Interactive Graphing Library. Disponível em: https://plotly.com/python/plotly-express/. Acesso em: 15 jun. 2025.

- MATPLOTLIB DEVELOPERS. Matplotlib - Python 2D plotting library. Disponível em: https://matplotlib.org/. Acesso em: 15 jun. 2025.

- PILLOW. Python Imaging Library (Pillow). Disponível em: https://python-pillow.org/. Acesso em: 15 jun. 2025.

- NUMPY DEVELOPERS. NumPy: Fundamental package for scientific computing. Disponível em: https://numpy.org/. Acesso em: 15 jun. 2025.

- PANDAS DEVELOPMENT TEAM. Pandas - Python Data Analysis Library. Disponível em: https://pandas.pydata.org/. Acesso em: 15 jun. 2025.

💻 Ambiente de Desenvolvimento

- GOOGLE. Google Colaboratory (Colab). Disponível em: https://colab.google/. Acesso em: 15 jun. 2025.
    """)
