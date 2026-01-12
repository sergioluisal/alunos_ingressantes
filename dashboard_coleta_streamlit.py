import streamlit as st
import pandas as pd
import requests
import os
import re
from PyPDF2 import PdfMerger
from zipfile import ZipFile
from io import BytesIO

# ---------------- CONFIGURAÇÃO ----------------
COLUNA_NOME = 'Nome'

COLUNAS_DOCS = [
    '1. Formulário de matrícula de aluno ingressante',
    '2. Carta de aceite definitivo',
    '3. Formulário de matrícula em disciplinas',
    '4. Recibo do depósito da taxa de inscrição',
    '5. Carta da instituição de origem, permitindo o afastamento total/parcial do candidato para cursar o Programa de Pós-Graduação (quando vinculado a alguma instituição/serviço) OU Carta informando a ausência de vínculo empregatício',
    '9. Carta da instituição de origem com liberação parcial ou total / ou / carta de ausência de vínculo empregatício',
    '6. Certidão de nascimento ou casamento',
    '4. Cédula de identidade (RG) ou Registro Nacional Migratório (RNM)',
    '5. CPF (caso o RG não possua o número)',
    '7. Comprovante de quitação eleitoral',
    '8. Certificado de reservista',
    '10. Diploma da Graduação',
    '11. Histórico Escolar do Curso de Graduação',
    '12. Diploma de Mestre (se houver)',
    '13. Histórico Escolar do Mestrado',
    '14. Atestado de conclusão de curso',
    '15. Se estrangeiro, passaporte e visto'
]

PASTA_SAIDA = "Pacotes_Matricula"

# ---------------- FUNÇÕES ----------------
def converter_link_drive(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return None
    try:
        file_id = re.search(r'/d/([a-zA-Z0-9-_]+)', str(url)).group(1)
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    except:
        return None

def processar_matriculas(df):
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    for index, row in df.iterrows():
        aluno = str(row[COLUNA_NOME]).strip().replace(" ", "_")
        merger = PdfMerger()
        arquivos_temp = []

        for i, col in enumerate(COLUNAS_DOCS):
            if col not in df.columns:
                continue

            url_download = converter_link_drive(row[col])

            if url_download:
                try:
                    r = requests.get(url_download, timeout=20)
                    temp_pdf = f"temp_{index}_{i}.pdf"
                    with open(temp_pdf, "wb") as f:
                        f.write(r.content)

                    merger.append(temp_pdf)
                    arquivos_temp.append(temp_pdf)
                except:
                    pass

        if arquivos_temp:
            merger.write(f"{PASTA_SAIDA}/{aluno}_Matricula_Completa.pdf")
            merger.close()

        for f in arquivos_temp:
            if os.path.exists(f):
                os.remove(f)

def criar_zip_em_memoria():
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zipf:
        for pasta, _, arquivos in os.walk(PASTA_SAIDA):
            for arquivo in arquivos:
                caminho = os.path.join(pasta, arquivo)
                zipf.write(caminho, arcname=arquivo)
    buffer.seek(0)
    return buffer

# ---------------- INTERFACE STREAMLIT ----------------
st.set_page_config(page_title="Consolidação de Matrículas", layout="centered")

st.title("📄 Consolidação de Documentos de Matrícula")
st.write("Faça upload da planilha e gere um **ZIP único** com todos os PDFs consolidados.")

arquivo = st.file_uploader(
    "📤 Envie a planilha (.xlsx ou .csv)",
    type=["xlsx", "csv"]
)

if arquivo:
    try:
        if arquivo.name.endswith(".xlsx"):
            df = pd.read_excel(arquivo)
        else:
            df = pd.read_csv(arquivo)

        df.columns = [c.strip().replace('\n', ' ') for c in df.columns]

        st.success("Planilha carregada com sucesso!")

        if st.button("⚙️ Processar documentos"):
            with st.spinner("Processando documentos..."):
                processar_matriculas(df)
                zip_buffer = criar_zip_em_memoria()

            st.success("Processamento concluído!")

            st.download_button(
                label="⬇️ Baixar ZIP com matrículas",
                data=zip_buffer,
                file_name="Pacotes_Matricula.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
