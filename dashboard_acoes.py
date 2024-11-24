import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard de Ações", layout="wide", page_icon="📈")

# Função para carregar os dados com cache atualizado
@st.cache_data
def carregar_dados(tickers):
    dados = []
    for ticker in tickers:
        df = yf.Ticker(ticker).history(period="1y")  # Dados dos últimos 1 ano
        df['Ticker'] = ticker  # Adiciona a coluna do ticker para identificar a empresa
        dados.append(df)
    return pd.concat(dados)

# Título do Dashboard
st.title("📈 Dashboard de Mercado de Ações")
st.markdown("### Acompanhe o desempenho de ações e índices de forma interativa!")

# Input do usuário para selecionar os tickers
st.sidebar.header("🔍 Selecione os Tickers")
lista_tickers = st.sidebar.text_input(
    "Digite os códigos das ações separados por vírgula (ex: ITUB4.SA, PETR4.SA):",
    value="^BVSP, ITUB4.SA, PETR4.SA, VALE3.SA"
)
tickers = [ticker.strip() for ticker in lista_tickers.split(",")]

# Carregar os dados das ações
st.sidebar.write("### 📥 Carregando dados...")
empresas = carregar_dados(tickers)

# Seção principal - Filtros e KPIs
st.sidebar.header("📊 Filtros de Visualização")
empresa_selecionada = st.sidebar.selectbox("Selecione a Empresa:", options=tickers)
dados_filtrados = empresas[empresas["Ticker"] == empresa_selecionada]

# Filtro de período
st.sidebar.header("📅 Filtro de Período")
periodo = st.sidebar.selectbox(
    "Selecione o período:",
    options=["5 dias", "1 mês", "2 meses", "3 meses", "6 meses", "1 ano"]
)

# Função para aplicar filtro de período
def filtrar_periodo(df, periodo):
    today = datetime.datetime.today()
    
    if periodo == "5 dias":
        delta = datetime.timedelta(days=5)
    elif periodo == "1 mês":
        delta = datetime.timedelta(days=30)
    elif periodo == "2 meses":
        delta = datetime.timedelta(days=60)
    elif periodo == "3 meses":
        delta = datetime.timedelta(days=90)
    elif periodo == "6 meses":
        delta = datetime.timedelta(days=180)
    elif periodo == "1 ano":
        delta = datetime.timedelta(days=365)
    
    data_filtro = today - delta

    # Ajustando para que o filtro funcione comparando com o índice sem fuso horário
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)  # Remove o fuso horário do índice
    
    return df[df.index >= data_filtro]

# Aplicar o filtro de período
dados_filtrados = filtrar_periodo(dados_filtrados, periodo)

# Cálculo de Variação Absoluta e Percentual
# A variação absoluta é calculada pela diferença entre o fechamento de hoje e o fechamento de ontem
# A variação percentual é calculada pela diferença entre os fechamentos dividida pelo fechamento de ontem

dados_filtrados['Variação Absoluta'] = dados_filtrados['Close'] - dados_filtrados['Close'].shift(1)
dados_filtrados['Variação Percentual'] = (dados_filtrados['Variação Absoluta'] / dados_filtrados['Close'].shift(1)) * 100

# Criar KPIs para destacar informações importantes
st.markdown("---")
st.subheader(f"📈 Preço Fechamento: {empresa_selecionada}")
kpi1, kpi2, kpi3, kpi4   = st.columns(4)

# Média de Volume
media_volume = dados_filtrados['Volume'].mean()

# Valores de KPI - Preço de Abertura, Fechamento, Volume
kpi1.metric("Preço Fechamento", f"R$ {dados_filtrados['Close'].iloc[-1]:.0f}")
kpi2.metric("Preço Abertura", f"R$ {dados_filtrados['Open'].iloc[0]:.0f}")
kpi3.metric("Preço Máximo", f"R$ {dados_filtrados['Close'].max():.0f}")
kpi4.metric("Preço Mínimo", f"R$ {dados_filtrados['Close'].min():.0f}")
#kpi5.metric("Preço Médio", f"R$ {dados_filtrados['Close'].mean():.2f}")
#kpi6.metric("Volume", f"{dados_filtrados['Volume'].mean():,.0f}")

# Calcular a Variação Absoluta e Percentual
var_abs = dados_filtrados['Variação Absoluta'].iloc[-1]
var_percent = dados_filtrados['Variação Percentual'].iloc[-1]

# Formatar a variação para exibição
var_abs_format = f"+{var_abs:.2f}" if var_abs > 0 else f"{var_abs:.2f}"
var_percent_format = f"({var_percent:.2f}%)"  # Exemplo de variação percentual formatada

# Mostrar a variação de valor
#st.markdown("### 📈 Variação do Dia")
kpi1.metric("Variação do Dia", var_abs_format, delta=var_percent_format)
kpi2.metric("Preço Médio", f"R$ {dados_filtrados['Close'].mean():.2f}")
kpi3.metric("Média de Volume", f"{media_volume:,.0f}")

# Gráfico de Preço Fechamento
st.markdown("---")
st.markdown("### 🔥 Gráficos de Desempenho")
fig_close = px.line(
    dados_filtrados, 
    x=dados_filtrados.index, 
    y="Close", 
    title=f"Preço de Fechamento - {empresa_selecionada}",
    template="plotly_dark",
    markers=True,
)
st.plotly_chart(fig_close, use_container_width=True)

# Gráfico de Volume
st.markdown("---")
st.subheader(f"📊 Volume de Negociação: {empresa_selecionada}")
fig_volume = px.bar(
    dados_filtrados, 
    x=dados_filtrados.index, 
    y="Volume", 
    title=f"Volume de Negociação - {empresa_selecionada}",
    template="plotly_dark",
    color_discrete_sequence=["#EF553B"],
)
st.plotly_chart(fig_volume, use_container_width=True)

# Média de Fechamento por Data
st.markdown("---")
st.markdown("### 🧮 Média de Fechamento por Data")
media_fechar = dados_filtrados.groupby(dados_filtrados.index.date)['Close'].mean()
fig_media_fechar = px.line(
    media_fechar,
    x=media_fechar.index,
    y=media_fechar.values,
    title="Média de Fechamento por Data",
    template="plotly_dark",
)
st.plotly_chart(fig_media_fechar, use_container_width=True)

# Variação Percentual por Data
st.markdown("---")
st.markdown("### 📉 Variação Percentual por Data")
dados_filtrados['Variação Percentual Acumulada'] = dados_filtrados['Variação Percentual'].cumsum()
fig_variacao_percentual = px.line(
    dados_filtrados,
    x=dados_filtrados.index,
    y='Variação Percentual Acumulada',
    title="Variação Percentual Acumulada por Data",
    template="plotly_dark",
)
st.plotly_chart(fig_variacao_percentual, use_container_width=True)

# Exibir a tabela de dados brutos
st.markdown("---")
st.markdown("### 📋 Tabela de Dados Brutos")
st.dataframe(dados_filtrados[['Open', 'Close', 'Volume', 'Variação Absoluta', 'Variação Percentual']], use_container_width=True)

# Estatísticas detalhadas na barra lateral
st.sidebar.header("📈 Estatísticas Detalhadas")
st.sidebar.write(dados_filtrados[['Close', 'Volume']].describe().round(2))

# Rodapé
st.markdown("---")
st.markdown(
    "📌 Criado por [Roger Costa](https://www.linkedin.com/in/roger-costa-49738a15b/) usando [Streamlit](https://streamlit.io/) e [Yahoo Finance](https://finance.yahoo.com/) ❤️"
)
