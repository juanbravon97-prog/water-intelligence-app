# 💧 Water Intelligence — Plataforma de Auditoría Hídrica Remota

Plataforma web para realizar auditorías hídricas a distancia, con formulario guiado por industria y chatbot inteligente integrado.

---

## 🚀 GUÍA DE DESPLIEGUE PASO A PASO

### Requisitos previos
- Una cuenta de GitHub (gratuita): https://github.com/signup
- Una cuenta de Streamlit Cloud (gratuita): https://share.streamlit.io
- Python 3.9+ instalado en tu computador (para pruebas locales)

---

### PASO 1: Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `water-intelligence-app`
3. Selecciona "Public" (necesario para Streamlit Cloud gratuito)
4. Marca "Add a README file"
5. Clic en "Create repository"

### PASO 2: Subir los archivos

**Opción A — Desde la web de GitHub (más fácil):**
1. En tu repositorio, clic en "Add file" → "Upload files"
2. Arrastra TODOS los archivos y carpetas de este proyecto
3. Clic en "Commit changes"
4. Repite para las carpetas (data/, pages/, .streamlit/)

**Opción B — Desde terminal (más rápido si sabes git):**
```bash
cd water-intelligence-app
git init
git add .
git commit -m "Initial commit - Water Intelligence platform"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/water-intelligence-app.git
git push -u origin main
```

### PASO 3: Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Clic en "New app"
3. Conecta tu cuenta de GitHub
4. Selecciona:
   - Repository: `TU_USUARIO/water-intelligence-app`
   - Branch: `main`
   - Main file path: `app.py`
5. Clic en "Deploy!"

**¡Listo! En 2-3 minutos tendrás tu app online** en una URL como:
`https://tu-usuario-water-intelligence-app.streamlit.app`

### PASO 4 (Opcional): Activar el chatbot con IA

El chatbot funciona en dos modos:
- **Modo gratuito** (por defecto): Respuestas inteligentes basadas en keywords. No necesita nada extra.
- **Modo IA**: Usa Claude de Anthropic para respuestas más naturales y contextuales.

Para activar el modo IA:
1. Obtén una API key en https://console.anthropic.com
2. En Streamlit Cloud, ve a tu app → Settings → Secrets
3. Agrega:
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-TU-KEY-AQUÍ"
```
4. Costo estimado: $1-5 USD/mes para uso normal

---

## 📁 Estructura del Proyecto

```
water-intelligence-app/
├── app.py                              ← Página principal (landing)
├── chatbot.py                          ← Módulo del chatbot (gratuito + IA)
├── requirements.txt                    ← Dependencias Python
├── README.md                           ← Este archivo
├── .streamlit/
│   └── config.toml                     ← Configuración visual de Streamlit
├── data/
│   └── industrias.json                 ← Templates de procesos por industria
└── pages/
    ├── 1_📋_Auditoría_Remota.py        ← Formulario guiado + chat
    └── 2_📊_Dashboard.py              ← Dashboard (post-auditoría)
```

---

## 🔧 Ejecución Local (para desarrollo)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`

---

## 📋 Cómo agregar una nueva industria

Edita el archivo `data/industrias.json` y agrega un bloque con la estructura:

```json
"clave_industria": {
    "nombre": "Nombre visible",
    "icono": "🏭",
    "procesos": [
        {
            "nombre": "Nombre del proceso",
            "tipo": "Consumidor | Generador | Ambos",
            "ce_max": 2.0,
            "hint": "Explicación para el usuario"
        }
    ],
    "bienvenida": "Mensaje del chatbot al seleccionar esta industria",
    "tips": ["Tip 1", "Tip 2"]
}
```

---

## 💰 Costos

| Componente | Costo |
|------------|-------|
| GitHub (repositorio) | Gratis |
| Streamlit Cloud (hosting) | Gratis (hasta 3 apps) |
| Dominio personalizado (opcional) | ~$12 USD/año |
| API de Claude para chatbot (opcional) | ~$1-5 USD/mes |
| **Total mínimo** | **$0 USD** |

---

## 🔒 Privacidad

Los datos ingresados por los clientes se almacenan en la sesión del navegador 
y en el CSV que descargan. No se guardan en ningún servidor externo.

Para almacenamiento persistente en producción, considerar:
- Google Sheets API (gratis, simple)
- Supabase (gratis hasta cierto volumen)
- Base de datos propia

---

*Water Intelligence · v2.0 · Abril 2026*
