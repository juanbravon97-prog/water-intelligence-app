@echo off
echo ============================================
echo  WATER INTELLIGENCE - Setup correcto
echo ============================================
echo.

REM 1. Verificar que estamos en la carpeta correcta
if not exist "app.py" (
    echo ERROR: No se encontro app.py
    echo Ejecuta este script DENTRO de la carpeta water-intelligence-app
    echo Primero haz: cd Downloads\water-intelligence-app\water-intelligence-app
    pause
    exit /b 1
)

echo Creando estructura de carpetas...

REM 2. Crear carpetas
if not exist "pages" mkdir pages
if not exist ".streamlit" mkdir .streamlit
if not exist "data" mkdir data

REM 3. Mover archivos a sus carpetas correctas
if exist "0_Calculadora_Gratuita.py" move "0_Calculadora_Gratuita.py" "pages\0_Calculadora_Gratuita.py"
if exist "1_Auditoria_Remota.py" move "1_Auditoria_Remota.py" "pages\1_Auditoria_Remota.py"
if exist "2_Dashboard.py" move "2_Dashboard.py" "pages\2_Dashboard.py"
if exist "config.toml" move "config.toml" ".streamlit\config.toml"
if exist "industrias.json" move "industrias.json" "data\industrias.json"

echo.
echo Estructura creada:
echo.
dir /b
echo.
echo pages\
dir /b pages
echo.
echo .streamlit\
dir /b .streamlit
echo.
echo data\
dir /b data
echo.

echo ============================================
echo  Ahora sube esto a GitHub
echo ============================================
echo.
echo Opcion 1 - Si tienes Git instalado, ejecuta:
echo   git add .
echo   git commit -m "Fix folder structure"
echo   git push
echo.
echo Opcion 2 - Desde GitHub web:
echo   1. Ve a github.com/juanbravon97-prog/water-intelligence-app
echo   2. Borra TODOS los archivos .py sueltos (0_Calculadora, 1_Auditoria, 2_Dashboard)
echo   3. Borra config.toml e industrias.json sueltos
echo   4. Crea carpeta pages/ y sube ahi los 3 .py
echo   5. Crea carpeta .streamlit/ y sube config.toml
echo   6. Crea carpeta data/ y sube industrias.json
echo.
pause
