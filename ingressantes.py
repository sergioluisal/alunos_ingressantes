import streamlit as st
import pandas as pd
import requests
import os
import re
from zipfile import ZipFile
from io import BytesIO
import time

# ---------------- CONFIGURAÇÃO ----------------
COLUNA_NOME = "Nome"
PASTA_SAIDA = "Pacotes_Matricula"

COLUNAS_DOCS = [
    '1. Formulário de matrícula de aluno ingressante',
    '2. Carta de aceite definitivo',
    '3. Formulário de matrícula em disciplinas',
    '4. Recibo do depósito da taxa de inscrição',
    '5. Carta da instituição de origem, permitindo o afastamento total/parcial do candidato para cursar o Programa de Pós-Graduação (quando vinculado a alguma instituição/serviço) OU Carta informando a ausência de vínculo empregatício',
    '9. Carta da instituição de origem com liberação parcial ou total / ou / carta de ausência de vínculo empregatício',
    '6. Certidão de nascimento ou casamento',
    '4. Cédula de identidade (RG) ou Registro Nacional Migratório (RNM) – Não será aceita carteira nacional de habilitação',
    '5. CPF (caso o RG não possua o número)',
    '7. Comprovante de quitação eleitoral',
    '8. Certificado de reservista (somente para brasileiros natos ou naturalizados do sexo masculino)',
    '10. Diploma da Graduação',
    '11. Histórico Escolar do Curso de Graduação',
    '12. Diploma de Mestre (se houver)',
    '13. Histórico Escolar do Mestrado, frente e verso (se houver)',
    '14. Atestado de conclusão de curso (para candidatos que concluíram o Ensino Superior e ainda não possuem o diploma)',
    '15. Se estrangeiro, arquivo único com página de identificação do passaporte (frente e verso) e visto'
]

# ---------------- FUNÇÕES ----------------
def converter_link_drive(url):
    if pd.isna(url) or "drive.google.com" not in str(url):
        return None
    try:
        file_id = re.search(r"/d/([a-zA-Z0-9-_]+)", str(url)).group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except:
        return None


def processar_matriculas(df):
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    erros = []

    for idx, row in df.iterrows():
        aluno = str(row[COLUNA_NOME]).strip().replace(" ", "_")
        pasta_aluno = os.path.join(PASTA_SAIDA, aluno)
        os.makedirs(pasta_aluno, exist_ok=True)

        for ordem, col in enumerate(COLUNAS_DOCS, start=1):
            if col not in df.columns:
                continue

            url_download = converter_link_drive(row[col])

            if url_download:
                try:
                    resposta = requests.get(url_download, timeout=30)
                    nome_pdf = f"{ordem:02d}_{col.split('.')[0].replace(' ', '_')}.pdf"
                    caminho_pdf = os.path.join(pasta_aluno, nome_pdf)

                    with open(caminho_pdf, "wb") as f:
                        f.write(resposta.content)

                    time.sleep(0.5)  # evita bloqueio do Drive

                except Exception as e:
                    erros.append(f"{aluno} - {col}")

    return erros


def criar_zip_em_memoria():
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zipf:
        for pasta, _, arquivos in os.walk(PASTA_SAIDA):
            for arquivo in arquivos:
                caminho = os.path.join(pasta, arquivo)
                zipf.write(
                    caminho,
                    arcname=os.path.relpath(caminho, PASTA_SAIDA)
                )
    buffer.seek(0)
    return buffer


# ---------------- INTERFACE STREAMLIT ----------------
st.set_page_config(page_title="Pacotes de Matrícula", layout="centered")

st.title("📦 Organização de Documentos de Matrícula")
st.write("Upload da planilha → Pastas por aluno → ZIP único para download")

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

        df.columns = [c.strip().replace("\n", " ") for c in df.columns]

        st.success("Planilha carregada com sucesso!")

        if st.button("⚙️ Processar documentos"):
            with st.spinner("Processando documentos dos alunos..."):
                erros = processar_matriculas(df)
                zip_buffer = criar_zip_em_memoria()

            st.success("Processamento concluído!")

            st.download_button(
                label="⬇️ Baixar ZIP com documentos",
                data=zip_buffer,
                file_name="Pacotes_Matricula.zip",
                mime="application/zip"
            )

            if erros:
                st.warning("Alguns documentos não puderam ser baixados:")
                st.write(erros)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

