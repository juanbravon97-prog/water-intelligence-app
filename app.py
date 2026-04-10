"""
╔══════════════════════════════════════════════════════════════╗
║  WATER INTELLIGENCE — Plataforma de Auditoría Hídrica       ║
║  Versión: 2.0                                                ║
║  Stack: Python + Streamlit + GitHub (datos en la nube)       ║
║                                                              ║
║  Para ejecutar localmente:                                   ║
║    pip install -r requirements.txt                           ║
║    streamlit run app.py                                      ║
║                                                              ║
║  Para desplegar en Streamlit Cloud:                          ║
║    1. Sube este repo a GitHub                                ║
║    2. Ve a share.streamlit.io                                ║
║    3. Conecta tu repo y despliega                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st

st.set_page_config(
    page_title="Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    
    .hero-container {
        background: linear-gradient(135deg, #1A1A18 0%, #14213D 50%, #0B6E4F 100%);
        border-radius: 16px;
        padding: 3rem 2.5rem;
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(16,163,127,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
    }
    .hero-sub {
        font-size: 1.1rem;
        opacity: 0.7;
        max-width: 600px;
        position: relative;
    }
    
    .feature-card {
        background: white;
        border: 1px solid #E0DED6;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: box-shadow 0.3s, transform 0.2s;
        height: 100%;
    }
    .feature-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
        transform: translateY(-2px);
    }
    .feature-icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
    .feature-title { font-size: 1.1rem; font-weight: 700; color: #1A1A18; margin-bottom: 0.4rem; }
    .feature-desc { font-size: 0.85rem; color: #6B6B63; line-height: 1.5; }
    
    .step-badge {
        background: #E6F5F0;
        color: #0B6E4F;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ───
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water.png", width=50)
    st.title("Water Intelligence")
    st.caption("Plataforma de Auditoría Hídrica Remota")
    st.divider()
    st.markdown("### 📍 Navegación")
    st.markdown("🏠 **Inicio** (estás aquí)")
    st.page_link("pages/0_Calculadora_Gratuita.py", label="⚡ Calculadora Gratuita")
    st.page_link("pages/1_Auditoria_Remota.py", label="📋 Auditoría Remota")
    st.page_link("pages/2_Dashboard.py", label="📊 Dashboard")
    st.divider()
    st.markdown("""
    <div style="background: #E6F5F0; border-radius: 8px; padding: 1rem; font-size: 0.8rem; color: #095C4B;">
        <strong>¿Necesitas ayuda?</strong><br>
        Contacta a tu consultor Water Intelligence o usa el chat dentro de la auditoría.
    </div>
    """, unsafe_allow_html=True)


# ─── Hero Section ───
st.markdown("""
<div class="hero-container">
    <div class="hero-title">💧 Water Intelligence</div>
    <div class="hero-sub">
        Plataforma de auditoría hídrica remota con asistente inteligente. 
        Complete el diagnóstico de su planta desde cualquier lugar — nosotros hacemos el análisis.
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Features ───
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📋</div>
        <div class="step-badge">PASO 1</div>
        <div class="feature-title">Auditoría Guiada</div>
        <div class="feature-desc">
            Complete el formulario paso a paso con la ayuda de nuestro asistente inteligente. 
            Procesos preconfigurados para su industria. Sin necesidad de ser experto en agua.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔬</div>
        <div class="step-badge">PASO 2</div>
        <div class="feature-title">Análisis Remoto</div>
        <div class="feature-desc">
            Nuestro equipo analiza sus datos, realiza el Water Pinch Analysis 
            y diseña las soluciones óptimas para su planta. Resultados en 48 horas.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="step-badge">PASO 3</div>
        <div class="feature-title">Dashboard Personalizado</div>
        <div class="feature-desc">
            Reciba su dashboard con KPIs, balance hídrico, huella hídrica 
            y recomendaciones priorizadas. Actualizable con sus propios datos.
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)

# CTA
col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
with col_cta2:
    if st.button("🚀  Comenzar Auditoría Remota", type="primary", use_container_width=True):
        st.switch_page("pages/1_Auditoria_Remota.py")

st.markdown("<br>", unsafe_allow_html=True)

# Industries supported
st.markdown("### Industrias que atendemos")
cols = st.columns(6)
industries = [("🥚", "Avícola"), ("🍄", "Champiñones"), ("🥛", "Láctea"), ("💧", "APR"), ("🌾", "Agricultura"), ("🏭", "Otra")]
for col, (icon, name) in zip(cols, industries):
    with col:
        st.markdown(f"""
        <div style="text-align:center; padding: 12px; background: white; border: 1px solid #E0DED6; border-radius: 10px;">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="font-size: 0.8rem; font-weight: 600; color: #3A3A36; margin-top: 4px;">{name}</div>
        </div>
        """, unsafe_allow_html=True)
