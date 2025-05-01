import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🌍 Mapa de Liderança Eleitoral - Amazonas")

# Caminhos fixos para colunas
COL_CODIGO = "CD_MUN"
COL_NOME = "NM_MUN"

def carregar_dados():
    df = pd.read_csv("PesquisaAmazonas_atualizado.csv")
    df.columns = df.columns.str.strip()
    df['COD_MUN'] = df['COD_MUN'].astype(str).str.zfill(7)

    # Calcular percentuais por município
    dist = df.groupby(['COD_MUN', 'Estim1_pref']).size().reset_index(name='votos')
    total = dist.groupby('COD_MUN')['votos'].transform('sum')
    dist['percentual'] = dist['votos'] / total

    # Pegar o candidato com maior percentual em cada município
    lideres = dist.sort_values(['COD_MUN', 'percentual'], ascending=[True, False])
    lideres = lideres.drop_duplicates('COD_MUN')
    lideres = lideres[['COD_MUN', 'Estim1_pref']].rename(columns={
        'Estim1_pref': 'lider'
    })

    # Ler shapefile e aplicar nomes fixos
    mapa = gpd.read_file("AM_Municipios_2024.shp")
    mapa['COD_MUN'] = mapa[COL_CODIGO].astype(str).str.zfill(7)
    mapa['nome_mun'] = mapa[COL_NOME].astype(str)

    # Mesclar
    mapa = mapa.merge(lideres, on='COD_MUN', how='left')
    mapa['aparece'] = mapa['lider'].notna()
    mapa['lider_david'] = mapa['lider'] == 'david_almeida'
    mapa['lider_omar'] = mapa['lider'] == 'omar_aziz'

    return mapa

mapa = carregar_dados()

aba = st.radio("Escolha o mapa que deseja visualizar:", [
    "1. Municípios com pesquisa",
    "2. Onde David Almeida lidera",
    "3. Onde Omar Aziz lidera"
])

fig, ax = plt.subplots(figsize=(10, 10))

# Exibir todos os municípios em cinza claro de fundo
mapa.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)

# Camada com dados específicos
if aba == "1. Municípios com pesquisa":
    selecionado = mapa[mapa['aparece']]
    selecionado.plot(ax=ax, color='orange', edgecolor='black', linewidth=0.5)
    ax.set_title("Municípios com dados de pesquisa", fontsize=14)
elif aba == "2. Onde David Almeida lidera":
    selecionado = mapa[mapa['lider_david']]
    selecionado.plot(ax=ax, color='green', edgecolor='black', linewidth=0.5)
    ax.set_title("Municípios onde David Almeida lidera", fontsize=14)
elif aba == "3. Onde Omar Aziz lidera":
    selecionado = mapa[mapa['lider_omar']]
    selecionado.plot(ax=ax, color='blue', edgecolor='black', linewidth=0.5)
    ax.set_title("Municípios onde Omar Aziz lidera", fontsize=14)

# Adicionar nomes apenas nos municípios com dados
for x, y, label in zip(selecionado.geometry.centroid.x,
                      selecionado.geometry.centroid.y,
                      selecionado['nome_mun']):
    ax.text(x, y, label, fontsize=4, ha='center', color='black')

ax.axis('off')
st.pyplot(fig)

st.caption("Fonte: Dados simulados da Projeta - Pesquisa de Mercado")
