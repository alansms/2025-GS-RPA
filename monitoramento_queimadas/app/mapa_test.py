import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
# Função de teste para visualizar os pontos do mapa
def main():
    st.title("Teste de Visualização do Mapa")
    # Criar dados de teste
    np.random.seed(42)
    num_pontos = 1000
    # Coordenadas aleatórias no Brasil
    latitude = np.random.uniform(-33.7, -5.2, num_pontos)
    longitude = np.random.uniform(-73.9, -34.8, num_pontos)
    # DataFrame de teste
    df = pd.DataFrame({
        'latitude': latitude,
        'longitude': longitude,
        'uf': np.random.choice(['SP', 'MG', 'RJ', 'PR', 'AM', 'PA'], num_pontos),
        'bioma': np.random.choice(['Amazônia', 'Cerrado', 'Mata Atlântica', 'Caatinga'], num_pontos)
    })
    # Mostrar alerta com instruções
    st.info("⚠️ **Aviso importante**: Aguarde o carregamento completo do mapa. Os pontos aparecem como círculos vermelhos grandes com borda branca.")
    # Opções de estilo de mapa
    map_styles = {
        "Carto Positron (Claro)": "carto-positron",
        "Carto Darkmatter (Escuro)": "carto-darkmatter",
        "Stamen Terrain": "stamen-terrain"
    }
    selected_style = st.selectbox("Estilo do mapa:", options=list(map_styles.keys()), index=1)
    # Criar mapa com pontos grandes e marcadores destacados
    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_name='uf',
        hover_data={'latitude': False, 'longitude': False, 'bioma': True},
        color_discrete_sequence=['#FF0000'],
        zoom=4,
        height=700
    )
    # Personalizar os marcadores para serem muito maiores e com borda
    fig.update_traces(
        marker=dict(
            size=40,
            color='#FF0000',
            opacity=1.0,
            line=dict(width=3, color='white')
        )
    )
    # Configurar layout
    fig.update_layout(
        mapbox_style=map_styles[selected_style],
        mapbox=dict(
            center=dict(lat=-15.8, lon=-47.9),
            zoom=4,
        ),
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    # Exibir mapa
    st.plotly_chart(fig, use_container_width=True)
    # Instruções
    with st.expander("Como usar o mapa"):
        st.markdown("""
        ### Instruções para visualizar os focos de queimadas:
        1. **Aguarde o carregamento completo** do mapa antes de interagir
        2. **Aumente o zoom no mapa** usando a roda do mouse ou os botões (+/-) no canto superior direito
        3. **Clique e arraste** para navegar pelo mapa
        4. **Passe o mouse sobre os pontos** para ver informações detalhadas
        5. **Experimente diferentes estilos de mapa** para melhorar a visualização
        Os pontos **vermelhos com borda branca** representam os focos de queimadas.
        """)
if __name__ == "__main__":
    main()
