"""
Calculadora Gratuita de Eficiencia Hídrica — Funnel de conversión
El usuario ingresa 4 datos → obtiene score → desbloquea con email → CTA a auditoría
Los leads se guardan en Google Sheets automáticamente (si está configurado)
"""

import streamlit as st
import json
import math
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Calculadora Gratuita | Water Intelligence", page_icon="⚡", layout="centered")

# ─── CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap');
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    
    .hero-banner {
        background: linear-gradient(135deg, #1A1A18 0%, #14213D 60%, #0B6E4F 100%);
        border-radius: 16px; padding: 2.5rem 2rem; color: white; text-align: center;
        margin-bottom: 1.5rem; position: relative; overflow: hidden;
    }
    .hero-banner h1 { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem; }
    .hero-banner p { font-size: 1rem; opacity: 0.65; max-width: 500px; margin: 0 auto; }
    .hero-badge { display: inline-block; background: rgba(16,163,127,0.2); color: #10A37F; padding: 4px 14px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 1rem; }
    
    .score-card { background: white; border: 1px solid #E0DED6; border-radius: 16px; padding: 2rem; text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04); margin-bottom: 1rem; }
    .score-grade { font-family: 'Playfair Display', serif; font-size: 4rem; font-weight: 800; line-height: 1; }
    .score-label { font-size: 0.85rem; color: #8A8A82; margin-top: 0.3rem; }
    
    .locked-card { background: white; border: 1px solid #E0DED6; border-radius: 12px; padding: 1.2rem;
        position: relative; overflow: hidden; margin-bottom: 0.8rem; }
    .locked-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.5); backdrop-filter: blur(8px);
        display: flex; align-items: center; justify-content: center; z-index: 2; }
    .locked-badge { background: #1A1A18; color: white; padding: 6px 16px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; }
    .blurred { filter: blur(8px); user-select: none; }
    
    .unlock-box { background: linear-gradient(135deg, #14213D, #0B6E4F); border-radius: 16px; padding: 2rem;
        text-align: center; color: white; margin: 1.5rem 0; }
    .unlock-box h3 { font-family: 'Playfair Display', serif; font-size: 1.3rem; margin-bottom: 0.5rem; }
    .unlock-box p { font-size: 0.85rem; opacity: 0.7; margin-bottom: 1rem; }
    
    .cta-card { background: white; border: 2px solid #0B6E4F; border-radius: 16px; padding: 2rem; text-align: center; margin-top: 1.5rem; }
    .cta-card h3 { font-family: 'Playfair Display', serif; font-size: 1.3rem; color: #1A1A18; margin-bottom: 0.5rem; }
    
    .metric-big { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; line-height: 1.1; }
    .metric-sub { font-size: 0.8rem; color: #8A8A82; margin-top: 0.2rem; }
    
    .social-proof { text-align: center; padding: 1.5rem; font-size: 0.75rem; color: #A3A39A; letter-spacing: 1.5px; }
</style>
""", unsafe_allow_html=True)

# ─── Google Sheets Integration ───
def save_lead_to_sheets(data: dict):
    """Guarda el lead en Google Sheets si las credenciales están configuradas."""
    try:
        creds_json = st.secrets.get("GOOGLE_SHEETS_CREDENTIALS", "")
        sheet_url = st.secrets.get("GOOGLE_SHEET_URL", "")
        if not creds_json or not sheet_url:
            return False
        
        import gspread
        from google.oauth2.service_account import Credentials
        
        creds_dict = json.loads(creds_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(credentials)
        
        sheet = gc.open_by_url(sheet_url).sheet1
        
        row = [
            datetime.now().isoformat(),
            data.get("email", ""),
            data.get("industry", ""),
            data.get("consumption", ""),
            data.get("production", ""),
            data.get("recycle_pct", ""),
            data.get("has_treatment", ""),
            data.get("score", ""),
            data.get("grade", ""),
            data.get("potential_savings", ""),
            data.get("source", "calculator"),
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        return False


# ─── Scoring Engine ───
BENCHMARKS = {
    "avicola": {"best": 5, "avg": 12, "worst": 25, "unit": "L/1000 huevos", "prod_unit": "miles de huevos/día", "savings_mult": 0.6},
    "champinones": {"best": 15, "avg": 22, "worst": 35, "unit": "L/kg", "prod_unit": "kg/día", "savings_mult": 0.55},
    "lactea": {"best": 1.5, "avg": 3.5, "worst": 8, "unit": "L/L leche", "prod_unit": "litros leche/día", "savings_mult": 0.65},
    "agricola": {"best": 200, "avg": 500, "worst": 1200, "unit": "L/kg fruta", "prod_unit": "kg fruta/día", "savings_mult": 0.4},
    "otro": {"best": 8, "avg": 18, "worst": 40, "unit": "L/kg producto", "prod_unit": "unidades/día", "savings_mult": 0.5},
}

def calculate_score(industry, consumption, production, recycle_pct, has_treatment):
    bench = BENCHMARKS.get(industry, BENCHMARKS["otro"])
    
    daily_liters = consumption * 1000
    intensity = daily_liters / production if production > 0 else bench["avg"]
    
    if intensity <= bench["best"]:
        score = 95
    elif intensity >= bench["worst"]:
        score = 15
    else:
        rng = bench["worst"] - bench["best"]
        position = (bench["worst"] - intensity) / rng
        score = round(15 + position * 80)
    
    if recycle_pct > 50: score = min(100, score + 10)
    elif recycle_pct > 20: score = min(100, score + 5)
    elif recycle_pct == 0: score = max(0, score - 10)
    
    if has_treatment == "No": score = max(0, score - 10)
    
    score = max(5, min(99, score))
    
    gap = max(0, intensity - bench["best"])
    potential_reduction = gap * bench["savings_mult"]
    potential_m3 = round((potential_reduction * production) / 1000)
    potential_money = round(potential_m3 * 1.2 * 30)
    potential_pct = round((potential_reduction / intensity) * 100) if intensity > 0 else 0
    
    grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"
    grade_color = "#0B6E4F" if score >= 80 else "#2E86AB" if score >= 60 else "#F18F01" if score >= 40 else "#E17055" if score >= 20 else "#C73E1D"
    
    return {
        "score": score, "intensity": round(intensity, 1), "unit": bench["unit"],
        "bench_best": bench["best"], "bench_avg": bench["avg"],
        "potential_m3": potential_m3, "potential_money": potential_money,
        "potential_pct": potential_pct, "grade": grade, "grade_color": grade_color,
        "quick_wins": "5-7" if score < 40 else "3-4" if score < 70 else "1-2",
        "roi_months": "6-12" if score < 40 else "12-18" if score < 70 else "18-24",
    }

# ─── Session State ───
if "calc_step" not in st.session_state:
    st.session_state.calc_step = "form"
if "calc_results" not in st.session_state:
    st.session_state.calc_results = None

# ─── Sidebar ───
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water.png", width=50)
    st.title("Water Intelligence")
    st.caption("Calculadora de Eficiencia Hídrica")
    st.divider()
    st.markdown("[🏠 Inicio](/)")
    st.markdown("⚡ **Calculadora** (estás aquí)")
    st.page_link("pages/1_Auditoria_Remota.py", label="📋 Auditoría Remota")
    st.page_link("pages/2_Dashboard.py", label="📊 Dashboard")

# ─── Hero Banner ───
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">⚡ Herramienta Gratuita</div>
    <h1>¿Cuánta agua está perdiendo tu planta?</h1>
    <p>Ingresa 4 datos y obtén un diagnóstico instantáneo con tu score de eficiencia hídrica y potencial de ahorro.</p>
</div>
""", unsafe_allow_html=True)

# ─── Calculator Form ───
st.markdown("### 📊 Calculadora de Eficiencia Hídrica")

with st.form("calculator_form"):
    # 1. Industry
    ind_options = {
        "avicola": "🥚 Avícola (huevos)",
        "champinones": "🍄 Champiñones",
        "lactea": "🥛 Láctea",
        "agricola": "🌾 Agricultura de riego",
        "otro": "🏭 Otra industria",
    }
    industry = st.selectbox("1. ¿Qué tipo de planta es?", options=list(ind_options.keys()), format_func=lambda x: ind_options[x])
    
    bench = BENCHMARKS[industry]
    
    # 2-3. Consumption and production
    col1, col2 = st.columns(2)
    with col1:
        consumption = st.number_input("2. Consumo de agua fresca (m³/día)", min_value=0.0, step=1.0, help="Revisa tu medidor general o tu boleta de agua")
    with col2:
        production = st.number_input(f"3. Producción diaria ({bench['prod_unit']})", min_value=0.0, step=1.0, help="Producción promedio diaria")
    
    # 4-5. Recycle and treatment
    col3, col4 = st.columns(2)
    with col3:
        recycle_pct = st.slider("4. ¿Qué % del agua reciclan?", 0, 100, 0, help="Si no reciclan, deja en 0")
    with col4:
        has_treatment = st.selectbox("5. ¿Tienen PTAR?", ["Sí", "No", "Parcial"])
    
    submitted = st.form_submit_button("⚡ Calcular mi Score de Eficiencia", type="primary", use_container_width=True)

if submitted and consumption > 0 and production > 0:
    results = calculate_score(industry, consumption, production, recycle_pct, has_treatment)
    st.session_state.calc_results = results
    st.session_state.calc_step = "results"
    
    # Save anonymous calculation
    save_lead_to_sheets({
        "email": "(anónimo)", "industry": industry, "consumption": consumption,
        "production": production, "recycle_pct": recycle_pct, "has_treatment": has_treatment,
        "score": results["score"], "grade": results["grade"],
        "potential_savings": results["potential_money"], "source": "calculator_anonymous"
    })

# ─── Results ───
if st.session_state.calc_results:
    results = st.session_state.calc_results
    
    st.divider()
    
    # Score - always visible
    st.markdown(f"""
    <div class="score-card">
        <div class="score-label">TU SCORE DE EFICIENCIA HÍDRICA</div>
        <div class="score-grade" style="color: {results['grade_color']}">{results['grade']}</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #3A3A36;">{results['score']} / 100</div>
        <div class="score-label" style="margin-top: 0.8rem;">
            Tu intensidad hídrica: <strong style="color: {results['grade_color']}">{results['intensity']} {results['unit']}</strong><br>
            Benchmark industria: mejor {results['bench_best']} · promedio {results['bench_avg']} {results['unit']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Locked cards
    is_locked = st.session_state.calc_step != "unlocked"
    
    if is_locked:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="locked-card">
                <div class="locked-overlay"><div class="locked-badge">🔒 Ingresa tu email</div></div>
                <div class="blurred">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #1A1A18; margin-bottom: 8px;">💰 Potencial de Ahorro Mensual</div>
                    <div class="metric-big" style="color: #0B6E4F;">${results['potential_money']:,} USD</div>
                    <div class="metric-sub">~{results['potential_m3']} m³/día recuperables</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="locked-card">
                <div class="locked-overlay"><div class="locked-badge">🔒 Ingresa tu email</div></div>
                <div class="blurred">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #1A1A18; margin-bottom: 8px;">📊 Diagnóstico Preliminar</div>
                    <div style="font-size: 0.85rem; color: #3A3A36; line-height: 1.6;">
                        Con un Water Pinch Analysis podríamos reducir tu consumo de agua fresca entre un 15-25%.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        for col, (title, value, sub) in zip([c1, c2, c3], [
            ("🔄 Reúso Recomendado", f"{min(70, recycle_pct + results['potential_pct'])}%", f"vs. actual: {recycle_pct}%"),
            ("⚡ Quick Wins", results['quick_wins'], "mejoras sin inversión"),
            ("📅 ROI Estimado", f"{results['roi_months']} meses", "retorno típico"),
        ]):
            with col:
                st.markdown(f"""
                <div class="locked-card">
                    <div class="locked-overlay"><div class="locked-badge">🔒</div></div>
                    <div class="blurred">
                        <div style="font-size: 0.75rem; font-weight: 600; color: #1A1A18;">{title}</div>
                        <div class="metric-big" style="color: #1B4965;">{value}</div>
                        <div class="metric-sub">{sub}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Email gate
        st.markdown("""<div class="unlock-box"><h3>🔓 Desbloquea tu diagnóstico completo</h3>
        <p>Ingresa tu email para ver tu potencial de ahorro y recomendaciones personalizadas.</p></div>""", unsafe_allow_html=True)
        
        with st.form("email_form"):
            email_col1, email_col2 = st.columns([3, 1])
            with email_col1:
                email = st.text_input("Email corporativo", placeholder="tu@empresa.cl", label_visibility="collapsed")
            with email_col2:
                unlock = st.form_submit_button("Desbloquear →", type="primary", use_container_width=True)
            
            if unlock and email and "@" in email:
                st.session_state.calc_step = "unlocked"
                # Save qualified lead
                save_lead_to_sheets({
                    "email": email, "industry": industry, "consumption": consumption,
                    "production": production, "recycle_pct": recycle_pct, "has_treatment": has_treatment,
                    "score": results["score"], "grade": results["grade"],
                    "potential_savings": results["potential_money"], "source": "calculator_qualified"
                })
                st.rerun()
        
        st.caption("Sin spam. Solo recibirás tu diagnóstico y una propuesta personalizada.")
    
    else:
        # UNLOCKED - Show everything
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="locked-card">
                <div style="font-size: 0.8rem; font-weight: 600; color: #1A1A18; margin-bottom: 8px;">💰 Potencial de Ahorro Mensual</div>
                <div class="metric-big" style="color: #0B6E4F;">${results['potential_money']:,} USD</div>
                <div class="metric-sub">~{results['potential_m3']} m³/día recuperables · {results['potential_pct']}% de mejora posible</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            diag = ("Tu planta tiene eficiencia por encima del promedio. Aún hay oportunidades en procesos específicos." if results['score'] >= 70 
                    else "Margen significativo de mejora. Un Water Pinch Analysis probablemente reduciría tu consumo 15-25% sin inversión mayor." if results['score'] >= 40
                    else "Oportunidad importante de optimización. Consumo muy por encima del benchmark — hay quick wins de alto impacto.")
            st.markdown(f"""
            <div class="locked-card">
                <div style="font-size: 0.8rem; font-weight: 600; color: #1A1A18; margin-bottom: 8px;">📊 Diagnóstico Preliminar</div>
                <div style="font-size: 0.85rem; color: #3A3A36; line-height: 1.6;">{diag}</div>
            </div>
            """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🔄 Reúso Recomendado", f"{min(70, recycle_pct + results['potential_pct'])}%", f"+{results['potential_pct']}% vs. actual")
        with c2:
            st.metric("⚡ Quick Wins", results['quick_wins'], "mejoras sin inversión")
        with c3:
            st.metric("📅 ROI Estimado", f"{results['roi_months']} meses", "retorno típico")
        
        # CTA
        st.markdown("""<div class="cta-card"><h3>¿Quieres el diagnóstico completo de tu planta?</h3>
        <p style="font-size: 0.9rem; color: #6B6B63;">Completa nuestra auditoría remota (15 min) y recibe un informe profesional con Water Pinch Analysis, balance hídrico y recomendaciones priorizadas.</p></div>""", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📋 Iniciar Auditoría Remota", type="primary", use_container_width=True):
                st.switch_page("pages/1_Auditoria_Remota.py")
        with col_b:
            st.link_button("📅 Agendar Videollamada", "https://calendly.com", use_container_width=True)

# Social proof
st.markdown("""
<div class="social-proof">
    INDUSTRIAS QUE CONFÍAN EN WATER INTELLIGENCE<br><br>
    🥚 Avícolas &nbsp;&nbsp; 🍄 Champiñones &nbsp;&nbsp; 🥛 Lácteas &nbsp;&nbsp; 💧 APR &nbsp;&nbsp; 🌾 Agricultura
</div>
""", unsafe_allow_html=True)
