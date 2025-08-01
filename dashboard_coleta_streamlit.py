import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import io

# Configuração da página
st.set_page_config(
    page_title="Acompanhamento de Suprimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLUNAS_DESEJADAS = [
    'MotivoDevolucao', 'Status', 'IdSolicitacaoRetirada', 'NumeroSerie',
    'CodigoModelo', 'PedidoDrl', 'OrdemColeta', 'Endereco', 'Complemento',
    'Cidade', 'Uf', 'DataSolicitacao', 'Coleta', 'Finalizado'
]

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame()

    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "csv":
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(uploaded_file, encoding=encoding, sep=";")
                    break
                except:
                    uploaded_file.seek(0)
            if df is None:
                raise Exception("Não foi possível ler o CSV com os encodings testados.")
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado.")
            return pd.DataFrame()

        if "DataSolicitacao" in df.columns:
            df["DataSolicitacao"] = pd.to_datetime(df["DataSolicitacao"], errors='coerce', dayfirst=True)

        if "Finalizado" in df.columns:
            df["Finalizado"] = pd.to_datetime(df["Finalizado"], errors='coerce')

        df = df.fillna("Não informado")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def safe_percentage(numerator, denominator):
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return 0
    return (numerator / denominator) * 100

def calculate_metrics(df):
    total_solicitacoes = len(df)

    if "Finalizado" in df.columns:
        finalizadas = df[~df["Finalizado"].isin(["Não informado", "", None])].shape[0]
    else:
        finalizadas = 0

    pendentes = total_solicitacoes - finalizadas
    taxa_finalizacao = safe_percentage(finalizadas, total_solicitacoes)
    return {
        "total_solicitacoes": total_solicitacoes,
        "coletas_finalizadas": finalizadas,
        "pendentes": pendentes,
        "taxa_finalizacao": taxa_finalizacao
    }

def create_bar_chart(df, x_col, title):
    counts = df[x_col].value_counts().head(10)
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        title=title,
        labels={'x': x_col, 'y': 'Quantidade'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(height=400, showlegend=False)
    return fig

def create_pie_chart(df, col, title):
    counts = df[col].value_counts()
    fig = px.pie(
        values=counts.values,
        names=counts.index,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(height=400)
    return fig


st.markdown("---")

uploaded_file = st.file_uploader("Faça upload do arquivo CSV ou Excel", type=["csv", "xls", "xlsx"])

st.markdown("""
    <h1 style='text-align: center; color: white; font-size: 48px;'>📊 Acompanhamento de Coletas</h1>
    <hr style='border: 1px solid #444;'>
""", unsafe_allow_html=True)
df = load_data(uploaded_file)

if df.empty:
    st.info("Por favor, envie um arquivo para começar.")
    st.stop()

st.sidebar.header("🔍 Filtros")
available_columns = df.columns.tolist()
df_filtered = df.copy()

for col in COLUNAS_DESEJADAS:
    if col in df_filtered.columns and df_filtered[col].nunique() < 100:
        options = ["Todos"] + sorted(df_filtered[col].unique().astype(str).tolist())
        selected = st.sidebar.selectbox(f"{col}:", options)
        if selected != "Todos":
            df_filtered = df_filtered[df_filtered[col].astype(str) == selected]

if "DataSolicitacao" in df_filtered.columns:
    min_date = df_filtered["DataSolicitacao"].min().date()
    max_date = df_filtered["DataSolicitacao"].max().date()
    start_date, end_date = st.sidebar.date_input("Período de Solicitação:", (min_date, max_date))
    df_filtered = df_filtered[
        (df_filtered["DataSolicitacao"].dt.date >= start_date) &
        (df_filtered["DataSolicitacao"].dt.date <= end_date)
    ]

metrics = calculate_metrics(df_filtered)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Solicitações", metrics["total_solicitacoes"])
with col2:
    st.metric("Coletas Finalizadas", metrics["coletas_finalizadas"])
with col3:
    st.metric("Pendentes", metrics["pendentes"])
with col4:
    st.metric("Taxa de Finalização", f"{metrics['taxa_finalizacao']:.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    if "MotivoDevolucao" in df_filtered.columns:
        st.plotly_chart(create_bar_chart(df_filtered, "MotivoDevolucao", "Devolução"), use_container_width=True)

with col2:
    if "Status" in df_filtered.columns:
        st.plotly_chart(create_pie_chart(df_filtered, "Status", "Status das Devoluções"), use_container_width=True)

st.subheader("📄 Dados Filtrados")
colunas_existentes = [col for col in COLUNAS_DESEJADAS if col in df_filtered.columns]
st.dataframe(df_filtered[colunas_existentes], use_container_width=True)

st.subheader("📥 Exportar Dados")
csv = df_filtered[colunas_existentes].to_csv(index=False, sep=";").encode("utf-8")
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

excel_buffer = io.BytesIO()
df_filtered[colunas_existentes].to_excel(excel_buffer, index=False, engine="openpyxl")
excel_buffer.seek(0)
st.download_button(
    label="Download Excel",
    data=excel_buffer,
    file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

with st.expander("ℹ️ Sobre os dados"):
    st.write("**Colunas presentes:**")
    for col in colunas_existentes:
        st.write(f"- {col}")
    st.write(f"**Total de registros:** {len(df_filtered)}")
