# -*- coding: utf-8 -*-
"""iip

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-Zl1PnSwS1BDsGwOPrJcbcSMvFtAWgMy
"""

#!pip install streamlit sentence_transformers
import pandas as pd
import numpy as np
import re
import altair as alt
from sentence_transformers import SentenceTransformer, util
import streamlit as st

st.title("¿CÓMO SE VIVE LA INNOVACIÓN PÚBLICA EN BOGOTÁ?")
st.markdown("Gracias al Índice de Innovación Pública IIP 2023 de **LABCapital - Veeduría Distrital** sabemos cómo están innovando las entidades distritales de Bogotá en los últimos años.")

@st.cache
def inicializar():
    iip = pd.read_csv("inno.csv", sep=',')

    def limpiarTexto(txt):
        return re.sub('[ ]+',' ',re.sub(r'[^a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ\.,; ]',r' ', txt)).strip()

    iip = iip.fillna("")
    iip['INNOVACION'] = iip['INNOVACION'].apply(limpiarTexto)
    iip['DESCRIPCION'] = iip['DESCRIPCION'].apply(limpiarTexto)

    iconos = {'Educación': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_educacion.png',
                      'Sector descentralizado territorialmente': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_descentralizado.png',
                      'Hábitat': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_habitat.png',
                      'Cultura, Recreación y Deporte': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_cultura_recre_deporte.png',
                      'Salud': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_salud.png',
                      'Órganos de Control': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_organo_control.png',
                      'Gobierno': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_gobierno.png',
                      'Gestión Pública': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_gestion_publica.png',
                      'Movilidad': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_movilidad.png',
                      'Hacienda': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_hacienda.png',
                      'Ambiente': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_ambiente.png',
                      'Desarrollo Económico, Industria y Turismo': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_desarrollo_eco_ind_turismo.png',
                      'Integración Social': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_integracion_social.png',
                      'Mujeres': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_mujeres.png',
                      'Planeación': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_planeacion.png',
                      'Seguridad, Convivencia y Justicia': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_seguridad_conviv_justicia.png',
                      'Gestión Juridíca': 'https://raw.githubusercontent.com/econb/iip/main/iconos/sec_gestion_juridica.png'}
    iconosdf = pd.DataFrame({'SECTOR':iconos.keys(), 'ICONO':iconos.values()})
    iip = pd.merge(iip, iconosdf, how='left')

    # Calculo de ubicacion de items en grilla.
    numColumnas = 3
    numItems = len(iip)
    filasIdx = np.floor(np.array(range(numItems))/numColumnas)*2+1
    colsIdx = [(i%numColumnas)-numColumnas for i in range(numItems)]

    # Modelo Transformer para convertir textos en vectores numericos (embeddings).
    myTransformer = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')
    lineasTexto = list((iip["INNOVACION"].apply(str.capitalize)+'. '+iip["DESCRIPCION"].apply(str.capitalize))) 
    lineasEmbeddings = myTransformer.encode(lineasTexto, convert_to_numpy=True, batch_size=30, show_progress_bar=True)

    return(iip, myTransformer, lineasEmbeddings, numColumnas, filasIdx, colsIdx)

iip, myTransformer, lineasEmbeddings, numColumnas, filasIdx, colsIdx = inicializar()

#===================================================
# RANKIN DE ITEMS SIMILARES A LA BUSQUEDA
#===================================================
termBusqueda = st.text_input("¿Qué temática de innovación en el distrito desea conocer?") 

resultados = iip.copy(deep=True)
if len(termBusqueda) > 2:
    # Embedding de termino de busqueda
    termBusqueda = str.lower(termBusqueda)
    busquedaEmbedding = myTransformer.encode(termBusqueda, convert_to_numpy=True)
    # Distancia coseno
    similaridad = [float(util.pytorch_cos_sim(busquedaEmbedding, lineaEmbeddings)) for lineaEmbeddings in lineasEmbeddings]
    # Indices de las lineas mas similares
    l = sorted(list(enumerate(similaridad)), key=lambda x:x[1], reverse=True)
    ordenSimilaridad = list(list(zip(*l))[0])
    # Filtrar los mas similares
    umbral = np.quantile(similaridad, q=0.98)
    n = sum(similaridad >= umbral)
    masSimilares = ordenSimilaridad[0:n]
    # Resultados filtrados
    resultados = resultados.iloc[masSimilares]

#===================================================
# VISUALIZACION DE RESULTADOS DE BUSQUEDA.
#===================================================

numColumnas = numColumnas
numResultados = len(resultados)
alturaGrilla = numResultados / numColumnas
resultados.insert(0,'j',colsIdx[0:numResultados])
resultados.insert(0,'i',filasIdx[0:numResultados])

fichas = alt.Chart(resultados).mark_rect(
    color='blue',
    opacity=0.0,
).encode(
    alt.X('j:O', axis=None),
    alt.Y('i:O', axis=None),
    tooltip=['INNOVACION','DESCRIPCION','ENTIDAD'],
).properties(
    width=700,
    height=100*alturaGrilla
)
imagenes = fichas.mark_image(
    opacity=0.3
).encode(
    url='ICONO'
)
textos = fichas.mark_text(
    size=13, color="black", baseline="line-bottom",
).transform_calculate(
    TEXTOFICHA="[slice(datum.INNOVACION,0,33)+'-',slice(datum.INNOVACION,33,66)+'-',slice(datum.INNOVACION,66,101)]"
).encode(
    text="TEXTOFICHA:O"
)

#fichas + imagenes + textos
st.altair_chart(fichas + imagenes + textos, use_container_width=True)
