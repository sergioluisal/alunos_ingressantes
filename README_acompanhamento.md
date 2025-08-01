Dashboard de Acompanhamento de Suprimentos

Visão Geral

Este dashboard interativo, construído com Streamlit, permite o acompanhamento e a análise de dados de suprimentos. Ele oferece funcionalidades de upload de arquivos (CSV e Excel), filtragem dinâmica por diversos campos e visualizações gráficas para facilitar a compreensão dos dados.

Funcionalidades

•
Upload de Dados: Carregue seus dados de suprimentos em formato CSV ou Excel.

•
Filtros Dinâmicos: Filtre os dados por:

•
MotivoDevolucao

•
Status

•
IdSolicitacaoRetirada

•
NumeroSerie

•
CodigoModelo

•
PedidoDrl

•
OrdemColeta

•
Endereco

•
Complemento

•
Cidade

•
Uf

•
DataSolicitacao (intervalo de datas)

•
Coleta

•
Finalizado

•
EstadoEntrega

•
StatusAtual

•
TipoProduto

•
DataPedido (intervalo de datas)



•
Métricas Principais: Visualize rapidamente o total de pedidos, pedidos entregues, quantidade total e taxa de entrega.

•
Visualizações Gráficas: Gráficos de barras, pizza e linha temporal para analisar:

•
Top 10 Pedidos por Estados

•
Status dos Pedidos

•
Evolução Temporal dos Pedidos

•
Top 10 Produtos por Tipo

•
Distribuição de Pedidos por Estado (mapa)

•
Pedidos Entregues e Não Entregues

•
Top 10 Produtos por Modelo



•
Exportação de Dados: Baixe os dados filtrados em formato CSV ou Excel.

Como Usar

1. Pré-requisitos

Certifique-se de ter o Python instalado em sua máquina. Recomenda-se usar um ambiente virtual.

2. Instalação das Dependências

Para instalar as bibliotecas necessárias, execute o seguinte comando no terminal:

Bash


pip install -r requirements.txt


3. Executando o Dashboard

Após instalar as dependências, execute o dashboard com o Streamlit:

Bash


streamlit run dashboard_acompanhamento_streamlit_aprimorado.py


Isso abrirá o dashboard em seu navegador padrão (geralmente em http://localhost:8501).

4. Carregando seus Dados

No dashboard, utilize o botão "Faça upload do seu arquivo CSV ou Excel" para carregar seu conjunto de dados. O dashboard processará o arquivo e exibirá as métricas e gráficos correspondentes.

5. Utilizando os Filtros

A barra lateral à esquerda contém todos os filtros disponíveis. Selecione as opções desejadas para refinar os dados exibidos no dashboard.

6. Exportando Dados

Na seção "Exportar Dados", você pode baixar o conjunto de dados atualmente filtrado em formato CSV ou Excel.

Estrutura do Projeto

•
dashboard_acompanhamento_streamlit_apprimorado.py: O código principal do aplicativo Streamlit.

•
requirements.txt: Lista de todas as dependências Python necessárias.

•
README_acompanhamento.md: Este arquivo de documentação.

Contribuição

Sinta-se à vontade para contribuir com melhorias, relatar bugs ou sugerir novas funcionalidades.

