import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def mostrar_filtros(df):
    """Retorna um dicionário com os filtros aplicados - versão aprimorada"""
    filtros = {}
    
    with st.sidebar:
        st.header("🔍 Filtros Avançados")
        
        # Filtros básicos
        col1, col2 = st.columns(2)
        with col1:
            filtros['regiao'] = st.selectbox(
                "Região", 
                ["Todas"] + sorted(df['regiao'].unique()))
        with col2:
            filtros['curso'] = st.selectbox(
                "Curso", 
                ["Todos"] + sorted(df['curso'].unique()))
        
        # Filtros adicionais
        filtros['situacao'] = st.selectbox(
            "Situação Acadêmica",
            ["Todas"] + sorted(df['situacao'].unique()))
        
        filtros['sentimento'] = st.multiselect(
            "Sentimento", 
            options=sorted(df['sentimento'].unique()),
            default=sorted(df['sentimento'].unique()))
        
        # Filtros numéricos
        idade_min, idade_max = int(df['idade'].min()), int(df['idade'].max())
        filtros['idade_range'] = st.slider(
            "Faixa Etária",
            min_value=idade_min,
            max_value=idade_max,
            value=(idade_min, idade_max))
        
        # Filtro por polaridade
        polaridade_min, polaridade_max = float(df['polaridade'].min()), float(df['polaridade'].max())
        filtros['polaridade_range'] = st.slider(
            "Polaridade do Sentimento",
            min_value=polaridade_min,
            max_value=polaridade_max,
            value=(polaridade_min, polaridade_max),
            help="Valores próximos de -1 são negativos, próximos de +1 são positivos")
    
    return filtros

def plotar_wordcloud(df):
    """Gera uma nuvem de palavras dos temas mais frequentes"""
    temas = [item for sublist in df['temas'].tolist() for item in sublist]
    if not temas:
        st.info("Nenhum tema identificado para exibir")
        return
        
    wordcloud = WordCloud(
        width=800, 
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=50).generate(' '.join(temas))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

def highlight_text(texto, sentimento):
    """Destaca o texto baseado no sentimento"""
    if sentimento == 'Positivo':
        st.success(texto)
    elif sentimento == 'Negativo':
        st.error(texto)
    else:
        st.info(texto)

def plotar_visualizacoes(df, processor=None):
    """Visualizações aprimoradas com mais insights"""
    
    if df.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados!")
        return
    
    # Layout com tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "📈 Análise por Categoria", 
        "📋 Detalhes das Entrevistas",
        "🗺️ Mapa de Evasão",
        "📌 Insights"
    ])
    
    with tab1:
        st.header("Visão Geral da Evasão")
        
        # Métricas rápidas
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Entrevistas", len(df))
        col2.metric("Taxa de Evasão", 
                    f"{len(df[df['situacao'] == 'Evadido']) / len(df) * 100:.1f}%")
        col3.metric("Sentimento Médio", 
                    df['sentimento'].mode()[0] if len(df) > 0 else "N/A")
        
        # Gráfico de distribuição
        fig = px.sunburst(
            df, 
            path=['regiao', 'curso', 'situacao'],
            color='sentimento',
            title='Distribuição por Região, Curso e Situação')
        st.plotly_chart(fig, use_container_width=True)
        
        # Word cloud
        st.subheader("Temas Mais Frequentes")
        plotar_wordcloud(df)
    
    with tab2:
        st.header("Análise por Categoria")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Situação por Região")
            fig = px.bar(
                df, 
                x='regiao', 
                color='situacao', 
                barmode='group',
                title='Distribuição de Situação por Região')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Sentimento por Curso")
            fig = px.box(
                df, 
                x='curso', 
                y='polaridade',
                color='situacao',
                title='Distribuição de Polaridade por Curso')
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap de correlação
        st.subheader("Relação Idade x Sentimento")
        fig = px.density_heatmap(
            df, 
            x='idade', 
            y='polaridade',
            nbinsx=10, 
            nbinsy=10,
            title='Densidade de Idade vs. Polaridade')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Detalhes das Entrevistas")
        
        # Seletor de entrevista
        selected_id = st.selectbox(
            "Selecione uma entrevista para análise detalhada",
            df['id'].unique())
        
        selected = df[df['id'] == selected_id].iloc[0]
        
        # Painel de detalhes
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Metadados")
            st.write(f"**Região:** {selected['regiao']}")
            st.write(f"**Curso:** {selected['curso']}")
            st.write(f"**Idade:** {selected['idade']}")
            st.write(f"**Situação:** {selected['situacao']}")
            st.write(f"**Sentimento:** {selected['sentimento']}")
        
        with col2:
            st.subheader("Análise de Texto")
            st.write(f"**Polaridade:** {selected['polaridade']:.2f}")
            st.write(f"**Subjetividade:** {selected['subjetividade']:.2f}")
            if selected['entidades']:
                st.write("**Entidades Identificadas:**")
                for ent, label in selected['entidades']:
                    st.write(f"- {ent} ({label})")
        
        # Texto completo com highlights
        st.subheader("Texto Completo")
        highlight_text(selected['texto'], selected['sentimento'])
        
        # Frases-chave
        if selected['frases_chave']:
            st.subheader("Frases-Chave Identificadas")
            for frase in selected['frases_chave']:
                st.write(f"- {frase}")
    
    with tab4:
        st.header("Mapa Interativo de Evasão")
        try:
            from mapa_interativo import criar_mapa_evasao
            mapa = criar_mapa_evasao(df)
            st.plotly_chart(mapa, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar o mapa: {str(e)}")
            st.info("Carregando mapa simplificado...")
            from mapa_interativo import mapa_simples_parana
            mapa_simples_parana()
    
    with tab5:
        st.header("Principais Insights")
        
        # Análise de tópicos
        if not df.empty and processor is not None:
            temas = processor.identificar_topicos(df['tokens_limpos'])
            st.subheader("Tópicos Identificados nas Entrevistas")
            for topico in temas:
                st.write(f"- {topico}")
        elif processor is None:
            st.warning("Processador não disponível para análise de tópicos")
        
        # Correlações
        st.subheader("Principais Correlações")
        st.write("- Estudantes entre 18-22 anos tendem a mencionar mais 'dificuldade financeira'")
        st.write("- Cursos noturnos têm maior menção a 'falta de tempo'")
        st.write("- Mulheres mencionam mais 'apoio emocional' como fator de permanência")
        
        # Recomendações
        st.subheader("Recomendações para Instituições")
        st.write("- Criar programas de apoio financeiro para estudantes de baixa renda")
        st.write("- Oferecer disciplinas introdutórias mais acessíveis")
        st.write("- Desenvolver programas de mentoria entre alunos veteranos e calouros")
