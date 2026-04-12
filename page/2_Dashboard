"""
Dashboard — Se genera después de completar la auditoría
"""

import streamlit as st

st.set_page_config(page_title="Dashboard | Water Intelligence", page_icon="📊", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Gestión Hídrica")

st.info("""
**Este dashboard se genera después de completar la auditoría.**

Una vez que envíes tu formulario de auditoría, nuestro equipo procesará tus datos 
y en 48 horas recibirás acceso a tu dashboard personalizado con:

- KPIs de consumo hídrico por proceso
- Balance de masa interactivo (diagrama Sankey)
- Monitoreo de calidad de agua
- Huella hídrica por unidad de producto (ISO 14046)
- Recomendaciones priorizadas con ROI estimado
""")

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Ir a la Auditoría", type="primary", use_container_width=True):
        st.switch_page("pages/1_Auditoria_Remota.py")
with col2:
    if st.button("🏠 Volver al Inicio", use_container_width=True):
        st.markdown('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)
