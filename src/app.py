import streamlit as st
import pandas as pd
import numpy as np
from data_processing import EntrevistaProcessor
from visualization import mostrar_filtros, plotar_visualizacoes
from gerador_entrevistas import GeradorEntrevistas
import time
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def carregar_dados():
    # Gera ou carrega dados fictícios
    gerador = GeradorEntrevistas(150)  # 150 entrevistas
    return gerador.gerar_dataframe()

def main():
    st.set_page_config(
        page_title="Análise de Evasão em Cursos TIC - Paraná",
        layout="wide",
        page_icon="📊"
    )
    
    # Barra de progresso para simular processamento
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"Carregando dados... {i+1}%")
        time.sleep(0.01)  # Simula processamento
    
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
    
    # Carregar e processar dados
    with st.spinner('Gerando dados fictícios...'):
        df = carregar_dados();
    
    with st.spinner('Processando entrevistas...'):
        try:
            processor = EntrevistaProcessor()
            resultados = []
            
            for idx, row in df.iterrows():
                serie_processada = processor.processar_entrevista(row)
                resultados.append(serie_processada)
                
            processed_data = df.join(pd.DataFrame(resultados), rsuffix='_processed')
            
            # Verificação de qualidade
            if processed_data.isnull().values.any():
                st.error("Dados processados contêm valores nulos - verifique o processamento")
                st.stop()
                
        except Exception as e:
            st.error(f"Falha crítica no processamento: {str(e)}")
            st.stop()
    
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
        
        # Aplicar filtros
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
            df_filtrado = df_filtrado[(df_filtrado['idade'] >= min_idade) & (df_filtrado['idade'] <= max_idade)]
        if filtros.get('polaridade_range'):
            min_pol, max_pol = filtros['polaridade_range']
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
    Orientador: Prof. Lisandro Rogério Modesto  
    Estudante: João Vitor de Souza Ribeiro  
    """)

if __name__ == "__main__":
    main()
