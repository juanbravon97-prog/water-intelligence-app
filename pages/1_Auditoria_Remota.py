}"""
Página de Auditoría Remota — Formulario guiado con chatbot integrado
"""

import streamlit as st
import json
import csv
import io
from pathlib import Path
from datetime import datetime

# Importar chatbot
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from chatbot import get_smart_response, get_ai_response

st.set_page_config(page_title="Auditoría Remota | Water Intelligence", page_icon="📋", layout="wide")

# ─── CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .step-header { background: #0B6E4F; color: white; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; }
    .step-title { font-size: 1.3rem; font-weight: 700; }
    .step-sub { font-size: 0.85rem; opacity: 0.8; }
    .hint-box { background: #FFF9E6; border-left: 3px solid #F18F01; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; font-size: 0.85rem; color: #6B6B63; margin-bottom: 1rem; }
    .chat-bot { background: #FFFFFF; border: 1px solid #E0DED6; border-radius: 4px 16px 16px 16px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.85rem; }
    .chat-user { background: #0B6E4F; color: white; border-radius: 16px 4px 16px 16px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.85rem; text-align: right; }
    .chat-label { font-size: 0.65rem; color: #0B6E4F; font-weight: 600; letter-spacing: 1px; margin-bottom: 2px; }
    .tip-card { background: #E6F5F0; border-radius: 8px; padding: 0.8rem 1rem; font-size: 0.85rem; color: #095C4B; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─── Load industry data ───
@st.cache_data
def load_industries():
    path = Path(__file__).parent.parent / "data" / "industrias.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

industries = load_industries()

# ─── Session State Init ───
if "audit_step" not in st.session_state:
    st.session_state.audit_step = 0
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}
if "selected_industry" not in st.session_state:
    st.session_state.selected_industry = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": "¡Hola! 👋 Soy tu asistente de Water Intelligence. Estoy aquí para ayudarte con cualquier duda mientras completas el formulario. Pregúntame lo que necesites sobre agua, procesos o los datos que te pedimos."}
    ]
if "processes_data" not in st.session_state:
    st.session_state.processes_data = []

STEPS = [
    ("🏭", "Tipo de Industria"),
    ("📋", "Datos Generales"),
    ("💧", "Fuente de Agua"),
    ("⚙️", "Procesos"),
    ("🔬", "Tratamiento"),
    ("🧪", "Calidad del Agua"),
    ("💰", "Costos"),
    ("📸", "Fotos y Docs"),
    ("✅", "Resumen y Envío"),
]

# ─── Sidebar: Navigation + Chat ───
with st.sidebar:
    st.title("💧 Auditoría Remota")
    
    # Progress
    progress = st.session_state.audit_step / (len(STEPS) - 1)
    st.progress(progress, text=f"Paso {st.session_state.audit_step + 1} de {len(STEPS)}")
    
    # Step navigation
    for i, (icon, name) in enumerate(STEPS):
        completed = i < st.session_state.audit_step
        active = i == st.session_state.audit_step
        label = f"{'✅' if completed else icon} {name}"
        if st.button(label, key=f"nav_{i}", disabled=i > st.session_state.audit_step, 
                     use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.audit_step = i
            st.rerun()
    
    st.divider()
    
    # Tips for current industry
    if st.session_state.selected_industry and st.session_state.selected_industry in industries:
        ind = industries[st.session_state.selected_industry]
        if ind.get("tips"):
            st.markdown("### 💡 Tips para tu industria")
            for tip in ind["tips"]:
                st.markdown(f'<div class="tip-card">{tip}</div>', unsafe_allow_html=True)


# ─── Main Content Area ───
main_col, chat_col = st.columns([3, 1])

with main_col:
    step = st.session_state.audit_step
    step_icon, step_name = STEPS[step]
    
    st.markdown(f"""
    <div class="step-header">
        <div class="step-title">{step_icon} Paso {step + 1}: {step_name}</div>
        <div class="step-sub">{'Selecciona tu industria para cargar procesos preconfigurados' if step == 0 else 'Completa los campos — el asistente en el chat puede ayudarte con cualquier duda'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ─── STEP 0: Industry Selection ───
    if step == 0:
        cols = st.columns(3)
        for i, (key, ind) in enumerate(industries.items()):
            with cols[i % 3]:
                selected = st.session_state.selected_industry == key
                if st.button(
                    f"{ind['icono']} {ind['nombre']}", 
                    key=f"ind_{key}", 
                    use_container_width=True,
                    type="primary" if selected else "secondary"
                ):
                    st.session_state.selected_industry = key
                    st.session_state.processes_data = [
                        {**p, "caudal_entrada": "", "caudal_salida": "", "ce_entrada": "", "ce_salida": ""}
                        for p in ind["procesos"]
                    ]
                    st.session_state.chat_history.append(
                        {"role": "bot", "text": ind["bienvenida"]}
                    )
                    st.session_state.audit_step = 1
                    st.rerun()
    
    # ─── STEP 1: General Data ───
    elif step == 1:
        with st.form("general_form"):
            c1, c2 = st.columns(2)
            with c1:
                company = st.text_input("Nombre de la empresa", value=st.session_state.audit_data.get("empresa", ""))
                contact = st.text_input("Nombre de contacto", value=st.session_state.audit_data.get("contacto", ""))
                phone = st.text_input("Teléfono", value=st.session_state.audit_data.get("telefono", ""))
            with c2:
                location = st.text_input("Ubicación (ciudad, región)", value=st.session_state.audit_data.get("ubicacion", ""))
                email = st.text_input("Email", value=st.session_state.audit_data.get("email", ""))
                production = st.text_input("Producción actual (ej: 500000 huevos/día)", value=st.session_state.audit_data.get("produccion", ""))
            
            if st.form_submit_button("Continuar →", type="primary"):
                st.session_state.audit_data.update({
                    "empresa": company, "ubicacion": location, "contacto": contact,
                    "email": email, "telefono": phone, "produccion": production
                })
                st.session_state.audit_step = 2
                st.session_state.chat_history.append(
                    {"role": "bot", "text": "✅ Datos generales guardados. Ahora necesito saber de dónde viene el agua que usa tu planta."}
                )
                st.rerun()
    
    # ─── STEP 2: Water Source ───
    elif step == 2:
        with st.form("water_form"):
            source = st.selectbox("Tipo de fuente de agua", 
                                  ["", "Pozo profundo", "Red pública / APR", "Río o canal", "Mixta (pozo + red)", "Otra"],
                                  index=0)
            source_detail = st.text_input("Detalle (profundidad del pozo, nombre del APR, etc.)")
            
            st.markdown('<div class="hint-box">💡 Si tienes medidor general, revisa cuántos m³ consumes al día. Si es pozo, multiplica: caudal de bomba (L/s) × 3.6 × horas de operación = m³/día</div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                consumption = st.text_input("Consumo total agua fresca (m³/día)")
            with c2:
                ce = st.text_input("CE del agua fresca (dS/m)")
            with c3:
                ph = st.text_input("pH del agua fresca")
            
            if st.form_submit_button("Continuar →", type="primary"):
                st.session_state.audit_data.update({
                    "fuente": source, "fuente_detalle": source_detail,
                    "consumo_fresca": consumption, "ce_fresca": ce, "ph_fresca": ph
                })
                st.session_state.audit_step = 3
                st.session_state.chat_history.append(
                    {"role": "bot", "text": "✅ Fuente de agua registrada. Ahora vamos a mapear cada proceso que consume o genera agua. Ya te cargué los procesos típicos de tu industria — ajusta los valores."}
                )
                st.rerun()
    
    # ─── STEP 3: Processes ───
    elif step == 3:
        st.markdown('<div class="hint-box">💡 Si no tienes medidor individual para un proceso, estima: ¿cuántas horas opera? ¿A qué caudal aproximado? Una estimación informada es mejor que dejarlo vacío.</div>', unsafe_allow_html=True)
        
        for i, proc in enumerate(st.session_state.processes_data):
            with st.expander(f"{'⚙️' if not proc.get('caudal_entrada') else '✅'} {proc['nombre']} — CE máx: {proc['ce_max']} dS/m", expanded=not proc.get("caudal_entrada")):
                if proc.get("hint"):
                    st.caption(f"ℹ️ {proc['hint']}")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    val = st.text_input("Entrada (m³/día)", value=proc.get("caudal_entrada", ""), key=f"in_{i}")
                    st.session_state.processes_data[i]["caudal_entrada"] = val
                with c2:
                    val = st.text_input("Salida (m³/día)", value=proc.get("caudal_salida", ""), key=f"out_{i}")
                    st.session_state.processes_data[i]["caudal_salida"] = val
                with c3:
                    val = st.text_input("CE entrada (dS/m)", value=proc.get("ce_entrada", ""), key=f"cei_{i}")
                    st.session_state.processes_data[i]["ce_entrada"] = val
                with c4:
                    val = st.text_input("CE salida (dS/m)", value=proc.get("ce_salida", ""), key=f"ceo_{i}")
                    st.session_state.processes_data[i]["ce_salida"] = val
        
        if st.button("Continuar →", type="primary"):
            st.session_state.audit_step = 4
            filled = sum(1 for p in st.session_state.processes_data if p.get("caudal_entrada"))
            st.session_state.chat_history.append(
                {"role": "bot", "text": f"✅ Procesos registrados ({filled} de {len(st.session_state.processes_data)} con datos). Ahora cuéntame sobre tu sistema de tratamiento de agua."}
            )
            st.rerun()
    
    # ─── STEP 4: Treatment ───
    elif step == 4:
        with st.form("treatment_form"):
            has_ptar = st.selectbox("¿Tienen planta de tratamiento (PTAR)?", ["", "Sí", "No", "Parcial"])
            
            treatment_type = ""
            capacity = ""
            has_recycling = ""
            recycled_vol = ""
            recycled_ce = ""
            
            if has_ptar in ["Sí", "Parcial"]:
                treatment_type = st.text_area("Describa las tecnologías de su PTAR",
                    placeholder="Ej: Coagulación-floculación, filtro de arena, UV, cloración...",
                    value=st.session_state.audit_data.get("tipo_tratamiento", ""))
                capacity = st.text_input("Capacidad de la PTAR (m³/día)", value=st.session_state.audit_data.get("capacidad_ptar", ""))
                has_recycling = st.selectbox("¿Reciclan agua actualmente?", ["", "Sí", "No"])
                if has_recycling == "Sí":
                    c1, c2 = st.columns(2)
                    with c1:
                        recycled_vol = st.text_input("Volumen reciclado (m³/día)")
                    with c2:
                        recycled_ce = st.text_input("CE del agua reciclada (dS/m)")
            
            if st.form_submit_button("Continuar →", type="primary"):
                st.session_state.audit_data.update({
                    "tiene_ptar": has_ptar, "tipo_tratamiento": treatment_type,
                    "capacidad_ptar": capacity, "recicla": has_recycling,
                    "vol_reciclado": recycled_vol, "ce_reciclada": recycled_ce
                })
                st.session_state.audit_step = 5
                st.session_state.chat_history.append(
                    {"role": "bot", "text": "✅ Tratamiento registrado. Ahora necesito datos de calidad del agua. Si tienes un análisis de laboratorio reciente, genial. Si no, valores aproximados también sirven."}
                )
                st.rerun()
    
    # ─── STEP 5: Quality ───
    elif step == 5:
        with st.form("quality_form"):
            st.markdown('<div class="hint-box">💡 Si tienes un PDF o imagen del análisis de laboratorio, súbelo abajo. Si no, ingresa los valores que conozcas.</div>', unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                q_ce = st.text_input("CE efluente (dS/m)")
            with c2:
                q_ph = st.text_input("pH efluente")
            with c3:
                q_turb = st.text_input("Turbidez (NTU)")
            with c4:
                q_dqo = st.text_input("DQO (mg/L)")
            
            st.markdown("**Parámetros para análisis de estruvita (si los conoce):**")
            c5, c6, c7, c8 = st.columns(4)
            with c5:
                q_nh4 = st.text_input("NH₄-N (mg/L)")
            with c6:
                q_po4 = st.text_input("PO₄-P (mg/L)")
            with c7:
                q_mg = st.text_input("Mg (mg/L)")
            with c8:
                q_ca = st.text_input("Ca (mg/L)")
            
            lab_file = st.file_uploader("📎 Subir análisis de laboratorio (PDF, imagen o Excel)", type=["pdf", "png", "jpg", "xlsx"])
            
            if st.form_submit_button("Continuar →", type="primary"):
                st.session_state.audit_data.update({
                    "ce_efluente": q_ce, "ph_efluente": q_ph, "turbidez": q_turb, "dqo": q_dqo,
                    "nh4_n": q_nh4, "po4_p": q_po4, "mg": q_mg, "ca": q_ca,
                })
                st.session_state.audit_step = 6
                st.session_state.chat_history.append(
                    {"role": "bot", "text": "✅ Calidad registrada. Casi terminamos — necesito los costos operativos para calcular el ROI de las mejoras."}
                )
                st.rerun()
    
    # ─── STEP 6: Costs ───
    elif step == 6:
        with st.form("costs_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                water_cost = st.text_input("Costo del agua fresca ($/m³ o $/mes)")
            with c2:
                chem_cost = st.text_input("Costo químicos PTAR ($/mes)")
            with c3:
                energy_cost = st.text_input("Costo energía PTAR ($/mes)")
            
            if st.form_submit_button("Continuar →", type="primary"):
                st.session_state.audit_data.update({
                    "costo_agua": water_cost, "costo_quimicos": chem_cost, "costo_energia": energy_cost
                })
                st.session_state.audit_step = 7
                st.session_state.chat_history.append(
                    {"role": "bot", "text": "✅ Costos registrados. Último paso opcional: si puedes subir fotos de tu planta, PTAR y equipos, nos ayuda mucho para el diagnóstico remoto."}
                )
                st.rerun()
    
    # ─── STEP 7: Photos ───
    elif step == 7:
        st.markdown("**Sube fotos de los siguientes elementos (opcional pero muy valioso):**")
        
        photos = {}
        photo_items = ["PTAR / sistema de tratamiento", "Estanques de acumulación", "Medidores de agua", "Equipos principales", "Vista general de la planta"]
        for item in photo_items:
            photos[item] = st.file_uploader(f"📸 {item}", type=["jpg", "png", "jpeg"], key=f"photo_{item}")
        
        notes = st.text_area("Notas adicionales", placeholder="Cualquier información que considere relevante para el diagnóstico...")
        
        if st.button("Continuar al resumen →", type="primary"):
            st.session_state.audit_data["notas"] = notes
            st.session_state.audit_step = 8
            st.session_state.chat_history.append(
                {"role": "bot", "text": "✅ ¡Excelente! Ya tienes todo listo. Revisa el resumen y envía el formulario. Recibirás tu diagnóstico preliminar en 48 horas."}
            )
            st.rerun()
    
    # ─── STEP 8: Review ───
    elif step == 8:
        ind_key = st.session_state.selected_industry
        ind = industries.get(ind_key, {})
        data = st.session_state.audit_data
        procs = st.session_state.processes_data
        
        st.markdown(f"### {ind.get('icono', '🏭')} {data.get('empresa', 'Sin nombre')} — {data.get('ubicacion', 'Sin ubicación')}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Datos generales:**")
            st.write(f"- Industria: {ind.get('nombre', 'N/A')}")
            st.write(f"- Producción: {data.get('produccion', 'N/A')}")
            st.write(f"- Contacto: {data.get('contacto', 'N/A')} ({data.get('email', 'N/A')})")
            st.write(f"- Fuente de agua: {data.get('fuente', 'N/A')}")
            st.write(f"- Consumo agua fresca: {data.get('consumo_fresca', 'N/A')} m³/día")
        with c2:
            st.markdown("**Tratamiento y calidad:**")
            st.write(f"- PTAR: {data.get('tiene_ptar', 'N/A')}")
            st.write(f"- Recicla agua: {data.get('recicla', 'N/A')}")
            st.write(f"- CE efluente: {data.get('ce_efluente', 'N/A')} dS/m")
            st.write(f"- Procesos registrados: {sum(1 for p in procs if p.get('caudal_entrada'))}")
            st.write(f"- Costo agua: {data.get('costo_agua', 'N/A')}")
        
        st.divider()
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Enviar Auditoría", type="primary", use_container_width=True):
                
                # ─── 1. ENVIAR A GOOGLE SHEETS via Apps Script ───
                try:
                    import urllib.request
                    import json as json_lib
                    
                    # REEMPLAZA con tu URL de Google Apps Script
                    SCRIPT_URL = st.secrets.get("APPS_SCRIPT_URL", "")
                    
                    if SCRIPT_URL:
                        # Preparar datos de procesos como texto
                        procs_text = "; ".join([
                            f"{p['nombre']}: {p.get('caudal_entrada','-')} m3/d in, {p.get('caudal_salida','-')} m3/d out"
                            for p in procs if p.get("caudal_entrada")
                        ])
                        
                        payload = json_lib.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "email": data.get("email", ""),
                            "industry": ind.get("nombre", ""),
                            "consumption": data.get("consumo_fresca", ""),
                            "production": data.get("produccion", ""),
                            "recycle_pct": "",
                            "treatment": data.get("tiene_ptar", ""),
                            "score": "",
                            "grade": "",
                            "savings": "",
                            "source": "auditoria_completa",
                            "empresa": data.get("empresa", ""),
                            "ubicacion": data.get("ubicacion", ""),
                            "contacto": data.get("contacto", ""),
                            "telefono": data.get("telefono", ""),
                            "fuente_agua": data.get("fuente", ""),
                            "ce_fresca": data.get("ce_fresca", ""),
                            "tipo_tratamiento": data.get("tipo_tratamiento", ""),
                            "ce_efluente": data.get("ce_efluente", ""),
                            "costo_agua": data.get("costo_agua", ""),
                            "procesos": procs_text,
                            "notas": data.get("notas", ""),
                            "notify_email": "true",
                        }).encode("utf-8")
                        
                        req = urllib.request.Request(
                            SCRIPT_URL, data=payload,
                            headers={"Content-Type": "application/json"}, method="POST"
                        )
                        urllib.request.urlopen(req, timeout=15)
                        sheets_ok = True
                    else:
                        sheets_ok = False
                except Exception as e:
                    sheets_ok = False
                
                # ─── 2. GENERAR PDF DIAGNÓSTICO PRELIMINAR ───
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.lib.units import inch, cm
                    from reportlab.lib.colors import HexColor
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
                    from reportlab.lib.enums import TA_CENTER, TA_LEFT
                    
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                        topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=2*cm, rightMargin=2*cm)
                    
                    styles = getSampleStyleSheet()
                    
                    # Custom styles
                    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                        fontSize=22, textColor=HexColor('#0B6E4F'), spaceAfter=6)
                    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'],
                        fontSize=11, textColor=HexColor('#8A8A82'), spaceAfter=20)
                    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                        fontSize=14, textColor=HexColor('#1A1A18'), spaceBefore=16, spaceAfter=8,
                        borderPadding=(0, 0, 0, 4), borderWidth=0, borderColor=HexColor('#0B6E4F'),
                        leftIndent=0)
                    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'],
                        fontSize=10, textColor=HexColor('#3A3A36'), leading=15, spaceAfter=6)
                    bold_style = ParagraphStyle('BoldBody', parent=body_style, 
                        fontName='Helvetica-Bold', textColor=HexColor('#1A1A18'))
                    small_style = ParagraphStyle('Small', parent=styles['Normal'],
                        fontSize=8, textColor=HexColor('#8A8A82'), spaceAfter=4)
                    
                    elements = []
                    
                    # Header
                    elements.append(Paragraph("💧 Water Intelligence", title_style))
                    elements.append(Paragraph("Diagnóstico Preliminar de Eficiencia Hídrica", subtitle_style))
                    elements.append(HRFlowable(width="100%", thickness=2, color=HexColor('#0B6E4F')))
                    elements.append(Spacer(1, 12))
                    
                    # Company info
                    elements.append(Paragraph("Datos de la Planta", heading_style))
                    
                    info_data = [
                        ["Empresa:", data.get("empresa", "N/A"), "Ubicación:", data.get("ubicacion", "N/A")],
                        ["Industria:", ind.get("nombre", "N/A"), "Producción:", data.get("produccion", "N/A")],
                        ["Contacto:", data.get("contacto", "N/A"), "Email:", data.get("email", "N/A")],
                        ["Fuente de agua:", data.get("fuente", "N/A"), "Consumo:", f"{data.get('consumo_fresca', 'N/A')} m³/día"],
                        ["PTAR:", data.get("tiene_ptar", "N/A"), "CE agua fresca:", f"{data.get('ce_fresca', 'N/A')} dS/m"],
                    ]
                    
                    info_table = Table(info_data, colWidths=[1.8*inch, 2.2*inch, 1.5*inch, 2*inch])
                    info_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#6B6B63')),
                        ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#6B6B63')),
                        ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#1A1A18')),
                        ('TEXTCOLOR', (3, 0), (3, -1), HexColor('#1A1A18')),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    elements.append(info_table)
                    elements.append(Spacer(1, 12))
                    
                    # Processes table
                    procs_with_data = [p for p in procs if p.get("caudal_entrada")]
                    if procs_with_data:
                        elements.append(Paragraph("Inventario de Procesos", heading_style))
                        
                        proc_header = ["Proceso", "Tipo", "Entrada m³/d", "Salida m³/d", "CE máx (dS/m)"]
                        proc_rows = [proc_header]
                        total_in = 0
                        total_out = 0
                        for p in procs_with_data:
                            inp = float(p.get("caudal_entrada", 0) or 0)
                            out = float(p.get("caudal_salida", 0) or 0)
                            total_in += inp
                            total_out += out
                            proc_rows.append([
                                p["nombre"], p["tipo"],
                                f"{inp:.1f}" if inp else "-",
                                f"{out:.1f}" if out else "-",
                                str(p.get("ce_max", "")),
                            ])
                        proc_rows.append(["TOTAL", "", f"{total_in:.1f}", f"{total_out:.1f}", ""])
                        
                        proc_table = Table(proc_rows, colWidths=[2.5*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.1*inch])
                        proc_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0B6E4F')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#E6F5F0')),
                            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0DED6')),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                        ]))
                        elements.append(proc_table)
                        elements.append(Spacer(1, 12))
                    
                    # Quick analysis
                    elements.append(Paragraph("Análisis Preliminar", heading_style))
                    
                    consumo = float(data.get("consumo_fresca", 0) or 0)
                    tiene_ptar = data.get("tiene_ptar", "")
                    recicla = data.get("recicla", "")
                    
                    # Generate observations
                    observations = []
                    if consumo > 0 and total_in > 0:
                        agua_no_contab = max(0, consumo - total_in)
                        pct_no_contab = (agua_no_contab / consumo * 100) if consumo > 0 else 0
                        if pct_no_contab > 10:
                            observations.append(f"⚠ Agua no contabilizada: {pct_no_contab:.0f}% del consumo total ({agua_no_contab:.0f} m³/día no está asignado a ningún proceso). Esto sugiere fugas, procesos no mapeados, o imprecisión en las estimaciones.")
                        else:
                            observations.append(f"✅ Balance hídrico razonablemente cerrado: {pct_no_contab:.0f}% de agua no contabilizada.")
                    
                    if tiene_ptar == "No":
                        observations.append("⚠ Sin planta de tratamiento: toda el agua residual se descarga sin tratar. Evaluar instalación de PTAR básica o al menos sistema de sedimentación.")
                    
                    if recicla == "No" or recicla == "":
                        observations.append("⚠ Sin reciclaje de agua: oportunidad significativa de reducir consumo de agua fresca reusando efluentes tratados en procesos de menor exigencia.")
                    elif recicla == "Sí":
                        observations.append("✅ Ya recicla agua — evaluar si se puede aumentar la tasa de reúso segregando corrientes por calidad.")
                    
                    ce_efl = data.get("ce_efluente", "")
                    if ce_efl:
                        try:
                            ce_val = float(ce_efl)
                            if ce_val > 3.0:
                                observations.append(f"⚠ CE del efluente elevada ({ce_val} dS/m). El agua reciclada necesita desalinización (NF o RO) antes de usarse en procesos sensibles.")
                            elif ce_val > 1.5:
                                observations.append(f"⚡ CE del efluente moderada ({ce_val} dS/m). Puede reusarse en procesos con CE tolerada > {ce_val} dS/m sin tratamiento adicional de sales.")
                            else:
                                observations.append(f"✅ CE del efluente baja ({ce_val} dS/m). Apta para reúso en la mayoría de procesos.")
                        except ValueError:
                            pass
                    
                    observations.append("📋 Próximo paso recomendado: agendar videollamada para revisar estos resultados y definir el plan de acción personalizado.")
                    
                    for obs in observations:
                        elements.append(Paragraph(obs, body_style))
                        elements.append(Spacer(1, 4))
                    
                    elements.append(Spacer(1, 20))
                    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#E0DED6')))
                    elements.append(Spacer(1, 8))
                    elements.append(Paragraph(f"Water Intelligence · Diagnóstico generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · Este es un análisis preliminar basado en los datos proporcionados.", small_style))
                    elements.append(Paragraph("Para el diagnóstico completo con Water Pinch Analysis, balance de masa y recomendaciones priorizadas, contacte a su consultor.", small_style))
                    
                    doc.build(elements)
                    pdf_bytes = pdf_buffer.getvalue()
                    pdf_ok = True
                except ImportError:
                    # reportlab not installed — generate simple text version
                    pdf_text = f"""WATER INTELLIGENCE — Diagnóstico Preliminar
{'='*50}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

DATOS DE LA PLANTA
Empresa: {data.get('empresa', 'N/A')}
Ubicación: {data.get('ubicacion', 'N/A')}
Industria: {ind.get('nombre', 'N/A')}
Producción: {data.get('produccion', 'N/A')}
Consumo agua fresca: {data.get('consumo_fresca', 'N/A')} m³/día
Fuente: {data.get('fuente', 'N/A')}
PTAR: {data.get('tiene_ptar', 'N/A')}
Recicla agua: {data.get('recicla', 'N/A')}

PROCESOS REGISTRADOS
"""
                    for p in procs:
                        if p.get("caudal_entrada"):
                            pdf_text += f"  - {p['nombre']}: {p.get('caudal_entrada','-')} m³/d entrada, {p.get('caudal_salida','-')} m³/d salida\n"
                    
                    pdf_text += f"""
ANÁLISIS PRELIMINAR
{'─'*40}
"""
                    for obs in observations:
                        pdf_text += f"{obs}\n\n"
                    
                    pdf_text += """
─────────────────────────────────────────
Water Intelligence · Gestión Hídrica Predictiva
Este es un análisis preliminar. Para el diagnóstico completo, contacte a su consultor.
"""
                    pdf_bytes = pdf_text.encode("utf-8")
                    pdf_ok = True
                except Exception as e:
                    pdf_ok = False
                    pdf_bytes = None
                
                # ─── 3. MOSTRAR RESULTADOS ───
                if sheets_ok:
                    st.success("✅ ¡Auditoría enviada exitosamente! Los datos fueron registrados y el equipo de Water Intelligence ha sido notificado.")
                else:
                    st.warning("⚠ Auditoría guardada localmente. Configure APPS_SCRIPT_URL en Streamlit Secrets para envío automático.")
                
                st.balloons()
                
                # Download buttons
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    if pdf_ok and pdf_bytes:
                        fname = f"diagnostico_{data.get('empresa','planta').replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}"
                        if isinstance(pdf_bytes, bytes) and pdf_bytes[:4] == b'%PDF':
                            st.download_button("📄 Descargar Diagnóstico (PDF)", data=pdf_bytes,
                                file_name=f"{fname}.pdf", mime="application/pdf")
                        else:
                            st.download_button("📄 Descargar Diagnóstico (TXT)", data=pdf_bytes,
                                file_name=f"{fname}.txt", mime="text/plain")
                with dl_col2:
                    # CSV backup
                    csv_output = io.StringIO()
                    csv_writer = csv.writer(csv_output)
                    csv_writer.writerow(["Campo", "Valor"])
                    csv_writer.writerow(["Fecha", datetime.now().isoformat()])
                    csv_writer.writerow(["Industria", ind.get("nombre", "")])
                    for k, v in data.items():
                        csv_writer.writerow([k, v])
                    csv_writer.writerow([])
                    csv_writer.writerow(["Proceso", "Tipo", "CE Max", "Entrada m3/d", "Salida m3/d", "CE entrada", "CE salida"])
                    for p in procs:
                        csv_writer.writerow([p["nombre"], p["tipo"], p["ce_max"], p.get("caudal_entrada",""), p.get("caudal_salida",""), p.get("ce_entrada",""), p.get("ce_salida","")])
                    
                    st.download_button("📥 Descargar datos (CSV)", data=csv_output.getvalue(),
                        file_name=f"auditoria_{data.get('empresa','planta').replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv")
        
        with col_btn2:
            if st.button("← Volver a editar", use_container_width=True):
                st.session_state.audit_step = 1
                st.rerun()
        
        st.markdown("""
        <div style="margin-top: 1rem; padding: 1rem; background: #E6F5F0; border-radius: 8px; font-size: 0.85rem; color: #095C4B;">
            <strong>¿Qué sigue?</strong><br>
            1. Nuestro equipo recibe tus datos automáticamente<br>
            2. Recibes un diagnóstico preliminar en PDF (descárgalo arriba)<br>
            3. Agendamos una videollamada para revisar resultados juntos<br>
            4. Entregamos el informe completo + dashboard en 2-3 semanas
        </div>
        """, unsafe_allow_html=True)


# ─── Chat Column ───
with chat_col:
    st.markdown("""
    <div style="background: #0B6E4F; color: white; padding: 10px 14px; border-radius: 10px 10px 0 0; font-size: 0.85rem; font-weight: 600;">
        💬 Asistente Water Intelligence
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container(height=450)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "bot":
                st.markdown(f'<div class="chat-label">ASISTENTE</div><div class="chat-bot">{msg["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg["text"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Escribe tu pregunta...", key="chat_input")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        
        # Try AI mode if API key is available
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
        industry_name = industries.get(st.session_state.selected_industry, {}).get("nombre", "")
        step_name = STEPS[st.session_state.audit_step][1]
        
        if api_key:
            response = get_ai_response(user_input, industry_name, step_name, api_key)
        else:
            response = get_smart_response(user_input, industry_name, step_name)
        
        st.session_state.chat_history.append({"role": "bot", "text": response})
        st.rerun()
