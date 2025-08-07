import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import plotly.express as px
import numpy as np

def criar_mapa_evasao(df):
    """Cria mapa interativo do Paraná com dados de evasão"""
    # Dados geográficos simplificados do Paraná
    parana_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Curitiba"},
                "geometry": {"type": "Point", "coordinates": [-49.25, -25.42]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Londrina"},
                "geometry": {"type": "Point", "coordinates": [-51.16, -23.31]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Maringá"},
                "geometry": {"type": "Point", "coordinates": [-51.93, -23.42]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Apucarana"},
                "geometry": {"type": "Point", "coordinates": [-51.46, -23.55]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Ponta Grossa"},
                "geometry": {"type": "Point", "coordinates": [-50.16, -25.09]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Cascavel"},
                "geometry": {"type": "Point", "coordinates": [-53.45, -24.96]}
            }
        ]
    }
    
    # Agregar dados por região
    if not df.empty:
        dados_regiao = df.groupby('regiao').agg({
            'id': 'count',
            'situacao': lambda x: (x == 'Evadido').mean(),
            'polaridade': 'mean'
        }).reset_index()
        
        dados_regiao.columns = ['regiao', 'total_entrevistas', 'taxa_evasao', 'sentimento_medio']
        
        # Criar mapa Plotly
        fig = px.scatter_geo(
            dados_regiao,
            lat=[-25.42, -23.31, -23.42, -23.55, -25.09, -24.96],  # Coordenadas aproximadas
            lon=[-49.25, -51.16, -51.93, -51.46, -50.16, -53.45],
            size='total_entrevistas',
            color='taxa_evasao',
            hover_name='regiao',
            hover_data=['sentimento_medio'],
            scope='south america',
            title='Mapa de Evasão no Paraná',
            color_continuous_scale='RdYlGn_r',  # Vermelho para alta evasão
            projection='mercator'
        )
        
        fig.update_geos(
            visible=False, resolution=50,
            showcountries=True, countrycolor="Black",
            showsubunits=True, subunitcolor="Blue"
        )
        
        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            coloraxis_colorbar={
                'title': 'Taxa de Evasão',
                'tickformat': '.0%'
            }
        )
        
        return fig
    else:
        return mapa_simples_parana()

def mapa_simples_parana():
    """Versão simplificada de fallback"""
    m = folium.Map(location=[-24.5, -51.5], zoom_start=7)
    
    cidades = {
        "Curitiba": [-25.42, -49.25],
        "Londrina": [-23.31, -51.16],
        "Maringá": [-23.42, -51.93],
        "Apucarana": [-23.55, -51.46],
        "Ponta Grossa": [-25.09, -50.16],
        "Cascavel": [-24.96, -53.45]
    }
    
    for cidade, coord in cidades.items():
        folium.Marker(
            location=coord,
            popup=f"{cidade}",
            tooltip=f"Clique para detalhes de {cidade}"
        ).add_to(m)
    
    return m

def main():
    st.title("Mapa de Evasão em Cursos TIC no Paraná")
    st.warning("Versão demonstrativa com dados fictícios")
    
    # Gerar dados fictícios para demonstração
    df = pd.DataFrame({
        'regiao': ['Curitiba', 'Londrina', 'Maringá', 'Apucarana', 'Ponta Grossa', 'Cascavel'] * 10,
        'situacao': np.random.choice(['Evadido', 'Formado', 'Cursando'], 60),
        'polaridade': np.random.uniform(-1, 1, 60)
    })
    
    mapa = criar_mapa_evasao(df)
    st.plotly_chart(mapa, use_container_width=True)

if __name__ == "__main__":
    main()
