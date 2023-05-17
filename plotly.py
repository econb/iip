import streamlit as st
import plotly.express as px

df = px.data.election()
fig = px.scatter_3d(df[0:10], x="Joly", y="Coderre", z="Bergeron", color="winner", size="total", hover_name="district",
                  symbol="result", color_discrete_map = {"Joly": "blue", "Bergeron": "green", "Coderre":"red"})
st.plotly_chart(fig)
