import streamlit as st
import plotly.express as px

col1, col2, col3 = st.columns(3)
col1.metric("Entidades participantes", 70)
col2.metric("Innovaciones diseñadas", 300)
col3.metric("Innovaciones implementadas", 210)

df = px.data.election()
fig = px.scatter_3d(df.sample(n=10), x="Joly", y="Coderre", z="Bergeron", color="winner", size="total", hover_name="district",
                  symbol="result", color_discrete_map = {"Joly": "blue", "Bergeron": "green", "Coderre":"red"})
st.plotly_chart(fig)
