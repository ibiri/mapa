import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("🌍 Mapa de Liderança Eleitoral - Amazonas (Folium)")

# Caminhos fixos para colunas
COL_CODIGO = "CD_MUN"
COL_NOME = "NM_MUN"

@st.cache_data
def carregar_dados():
    df = pd.read_csv("PesquisaAmazonas_atualizado.csv")
    df.columns = df.columns.str.strip()
    df['COD_MUN'] = df['COD_MUN'].astype(str).str.zfill(7)

    dist = df.groupby(['COD_MUN', 'Estim1_pref']).size().reset_index(name='votos')
    total = dist.groupby('COD_MUN')['votos'].transform('sum')
    dist['percentual'] = dist['votos'] / total

    lideres = dist.sort_values(['COD_MUN', 'percentual'], ascending=[True, False])
    lideres = lideres.drop_duplicates('COD_MUN')
    lideres = lideres[['COD_MUN', 'Estim1_pref', 'percentual']].rename(columns={
        'Estim1_pref': 'lider'
    })

    with open("amazonas_municipios_simples.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    return lideres, geojson_data

lideres, geojson_data = carregar_dados()

aba = st.radio("Escolha o mapa que deseja visualizar:", [
    "1. Municípios com pesquisa",
    "2. Onde David Almeida lidera",
    "3. Onde Omar Aziz lidera"
])

# Criar o mapa centralizado no Amazonas
m = folium.Map(location=[-3.1, -60], zoom_start=5)

# Criar dicionário para facilitar acesso
lider_dict = lideres.set_index('COD_MUN').to_dict(orient='index')

# Cores por aba
def get_color(lider):
    if aba == "1. Municípios com pesquisa":
        return "orange"
    elif aba == "2. Onde David Almeida lidera" and lider == "david_almeida":
        return "green"
    elif aba == "3. Onde Omar Aziz lidera" and lider == "omar_aziz":
        return "blue"
    return "lightgray"

# Adicionar polígonos ao mapa
for feature in geojson_data["features"]:
    props = feature["properties"]
    cod = props.get(COL_CODIGO)
    nome = props.get(COL_NOME)
    info = lider_dict.get(str(cod))

    if info:
        lider = info['lider']
        perc = round(info['percentual'] * 100, 1)
        tooltip = f"{nome} - {lider} ({perc}%)"
    else:
        lider = None
        tooltip = nome

    color = get_color(lider)

    folium.GeoJson(
        feature,
        tooltip=tooltip,
        style_function=lambda feat, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7 if color != 'lightgray' else 0.1
        }
    ).add_to(m)

st_folium(m, width=900, height=600)
st.caption("Fonte: Projeta")