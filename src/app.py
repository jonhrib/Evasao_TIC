import streamlit as st
import pandas as pd
import numpy as np
import time
import nltk

# Configuração da página DEVE SER A PRIMEIRA COISA
st.set_page_config(
    page_title="Análise de Evasão em Cursos TIC - Paraná",
    layout="wide",
    page_icon="📊"
)

# Agora importar os outros módulos
from data_processing import EntrevistaProcessor
from visualization import mostrar_filtros, plotar_visualizacoes
from gerador_entrevistas import GeradorEntrevistas

def carregar_dados():
    # Gera ou carrega dados fictícios
    gerador = GeradorEntrevistas(150)  # 150 entrevistas
    return gerador.gerar_dataframe()

def main():
    # Cabeçalho profissional
    st.title("📊 Painel de Análise de Evasão em Cursos TIC")
    st.markdown("""
    <style>
    .big-font {
        font-size:16px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-font">Visualização interativa dos fatores de evasão e permanência em cursos de Tecnologia da Informação e Comunicação no Paraná</p>', unsafe_allow_html=True)
    
    st.warning("⚠️ Trabalhando com dados fictícios para desenvolvimento - aguardando dados reais do TCC")
    
    # Download NLTK data (fazer apenas uma vez)
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        st.warning("Não foi possível baixar dados do NLTK, continuando...")
    
    # Barra de progresso para simular processamento
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"Carregando dados... {i+1}%")
        time.sleep(0.01)  # Simula processamento
    
    # Carregar e processar dados
    with st.spinner('Gerando dados fictícios...'):
        df = carregar_dados()
    
    with st.spinner('Processando entrevistas...'):
        try:
            processor = EntrevistaProcessor()
            resultados = []
            
            # Processar apenas uma amostra para teste inicial
            sample_df = df.head(50)  # Processar apenas 50 primeiras para teste
            
            for idx, row in sample_df.iterrows():
                serie_processada = processor.processar_entrevista(row)
                resultados.append(serie_processada)
                
            processed_data = sample_df.join(pd.DataFrame(resultados), rsuffix='_processed')
            
            # Verificação de qualidade
            if processed_data.isnull().values.any():
                st.warning("Alguns dados processados contêm valores nulos - continuando com dados limitados")
                # Preencher valores nulos
                processed_data = processed_data.fillna({
                    'temas': [],
                    'sentimento': 'Neutro',
                    'entidades': [],
                    'polaridade': 0,
                    'subjetividade': 0,
                    'frases_chave': [],
                    'tokens_limpos': ''
                })
                
        except Exception as e:
            st.error(f"Falha no processamento: {str(e)}")
            # Criar dados de fallback
            fallback_data = {
                'temas': [[]] * len(df),
                'sentimento': ['Neutro'] * len(df),
                'entidades': [[]] * len(df),
                'polaridade': [0] * len(df),
                'subjetividade': [0] * len(df),
                'frases_chave': [[]] * len(df),
                'tokens_limpos': [''] * len(df)
            }
            processed_data = df.join(pd.DataFrame(fallback_data, index=df.index))
    
    progress_bar.empty()
    status_text.empty()
    
    # Mostrar resumo dos dados
    if st.checkbox("Mostrar resumo dos dados"):
        st.subheader("Resumo Estatístico")
        st.dataframe(processed_data.describe(include='all'))
    
    # Seção de filtros e visualizações
    try:
        filtros = mostrar_filtros(processed_data)
        df_filtrado = processed_data.copy()
        
        # Aplicar filtros COM INDENTAÇÃO CORRETA
        if filtros.get('regiao') and filtros['regiao'] != "Todas":
            df_filtrado = df_filtrado[df_filtrado['regiao'] == filtros['regiao']]
        if filtros.get('curso') and filtros['curso'] != "Todos":
            df_filtrado = df_filtrado[df_filtrado['curso'] == filtros['curso']]
        if filtros.get('situacao') and filtros['situacao'] != "Todas":
            df_filtrado = df_filtrado[df_filtrado['situacao'] == filtros['situacao']]
        if filtros.get('sentimento'):
            df_filtrado = df_filtrado[df_filtrado['sentimento'].isin(filtros['sentimento'])]
        if filtros.get('idade_range'):
            min_idade, max_idade = filtros['idade_range']
            # Validar se os valores são diferentes
            if min_idade != max_idade:
                df_filtrado = df_filtrado[(df_filtrado['idade'] >= min_idade) & (df_filtrado['idade'] <= max_idade)]
        if filtros.get('polaridade_range'):
            min_pol, max_pol = filtros['polaridade_range']
            # Validar se os valores são diferentes
            if min_pol != max_pol:
                df_filtrado = df_filtrado[(df_filtrado['polaridade'] >= min_pol) & (df_filtrado['polaridade'] <= max_pol)]
        
        # Visualizações
        plotar_visualizacoes(df_filtrado)
        
    except Exception as e:
        st.error(f"Erro na aplicação de filtros ou visualizações: {str(e)}")
    
    # Rodapé profissional
    st.markdown("---")
    st.markdown("""
    **Sobre este painel:**  
    Desenvolvido como parte do projeto de TCC e estágio em Ciência da Computação na UNESPAR - Campus Apucarana.  
    Orientador: Prof. Dr. Lisandro Rogério Modesto  
    Estudante: João Vitor de Souza Ribeiro  
    """)

if __name__ == "__main__":
    main()
