# 🥇 TAV3-ST-QQE GOLD - App Web

App web profesional para análisis del Oro (XAU/USD) con triple confirmación:
**A-V2 Trend + Supertrend + QQE Mod + Filtro Tendencia Diaria + ADX**

Datos 100% reales desde Yahoo Finance. Gráfico interactivo con herramientas de dibujo, zoom y múltiples temporalidades.

---

## 🚀 OPCIÓN A: Desplegar en Streamlit Cloud (GRATIS, 10 minutos)

Esto te dará una **URL pública** que podrás abrir desde cualquier dispositivo.

### Paso 1: Crear cuenta en GitHub (si no tienes)
1. Ir a https://github.com/signup
2. Crear cuenta con tu email (gratis)
3. Verificar email

### Paso 2: Crear un repositorio nuevo
1. En GitHub, click en el botón verde **"New"** (o ir a https://github.com/new)
2. Nombre del repo: `tav3-gold-app`
3. Marcar como **Public** (debe ser público para Streamlit Cloud gratis)
4. NO marques "Add a README"
5. Click en **"Create repository"**

### Paso 3: Subir los archivos
**Opción más fácil (drag & drop):**
1. En la página del repo recién creado, click en **"uploading an existing file"**
2. Arrastra estos archivos del ZIP:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Para la carpeta `.streamlit/`, click en "create new file" y escribe `.streamlit/config.toml` (eso crea la carpeta), pega el contenido y guarda
4. Click en **"Commit changes"**

### Paso 4: Desplegar en Streamlit Cloud
1. Ir a https://share.streamlit.io/
2. Login con tu cuenta de GitHub (botón "Continue with GitHub")
3. Click en **"New app"** (esquina superior derecha)
4. Selecciona:
   - **Repository:** `tu-usuario/tav3-gold-app`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click en **"Deploy!"**
6. Espera 2-3 minutos mientras instala dependencias

### Paso 5: ¡Listo!
Tu app estará en una URL como:
```
https://tav3-gold-app-tu-usuario.streamlit.app
```
Esa URL es **pública** y la puedes abrir desde tu PC, móvil o tablet. Sin instalar nada, sin límites de TradingView.

---

## 💻 OPCIÓN B: Correr localmente en tu PC

Si prefieres correrlo en tu computadora sin internet:

### 1. Instalar Python (si no lo tienes)
- Windows/Mac: https://www.python.org/downloads/ (versión 3.10 o superior)
- Marca la casilla "Add Python to PATH" durante la instalación

### 2. Instalar dependencias
Abre terminal/CMD en la carpeta del ZIP descomprimido y ejecuta:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la app
```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 🎨 Funcionalidades de la App

### Datos
- ✅ **100% reales** desde Yahoo Finance
- ✅ Símbolos: GC=F (Gold Futures), XAUUSD=X (Spot), GLD (ETF)
- ✅ Auto-refresh cada 60 segundos

### Temporalidades
1m | 3m ⭐ | 5m | 15m | 30m | 1h | 4h | 1d

### Gráfico Plotly Interactivo
- 🔍 **Zoom**: rueda del mouse o click+arrastrar
- ✋ **Pan**: arrastrar el gráfico
- ✏️ **Herramientas de dibujo** (en la barra superior):
  - Línea
  - Rectángulo
  - Círculo
  - Lápiz libre
  - Path cerrado
  - Borrador
- 📷 **Descargar imagen** del gráfico en PNG
- 🎯 **Hover** con info detallada de cada vela
- 🌙 Tema oscuro profesional

### Indicadores integrados
- 📈 **A-V2 Trend** (Heikin Ashi + VWMA suavizado)
- 📊 **Supertrend** (parámetros ajustables)
- 🎯 **QQE Mod** (RSI + Bollinger)
- 💪 **ADX** con DI+ y DI- (subgráfico inferior)
- 📅 **Filtro tendencia diaria** (EMA 20/50)

### Panel de Métricas
- Tendencia diaria
- ADX (fuerza)
- Estado de cada confirmación
- **FUERZA TOTAL 0-100%** con recomendación clara:
  - ≥80% → ✅ OPERAR
  - 60-79% → ⚠️ ESPERAR
  - <60% → ❌ NO OPERAR

### Señales BUY/SELL
- 🟢 Triángulo verde abajo = BUY
- 🔴 Triángulo rojo arriba = SELL
- Solo aparecen con triple confirmación + tendencia diaria a favor + ADX fuerte
- Lista de últimas 20 señales en tabla expandible

---

## ❓ Preguntas frecuentes

**¿Es gratis?**
Sí, completamente. Streamlit Cloud Community es gratis para apps públicas. Yahoo Finance es gratis.

**¿Cuántos gráficos puedo abrir?**
Ilimitados. Sin restricciones de TradingView.

**¿Los datos son en tiempo real?**
Yahoo Finance tiene un delay de ~15 minutos para datos intraday. Para datos truly real-time, necesitarías un broker API (futuro upgrade).

**¿Puedo modificar los parámetros del indicador?**
Sí, todos están en el sidebar (MA period, ATR, ADX threshold, etc.)

**¿Puedo agregar alertas?**
Por ahora solo visuales. Para alertas por email/Telegram, sería un upgrade futuro.

**¿Qué hago si Yahoo no carga datos?**
1. Refresca con el botón "🔄 Actualizar"
2. Cambia de temporalidad
3. Verifica que el mercado esté abierto (Forex 24/5, Futuros casi 24/5)

---

## 📞 Soporte

Si tienes problemas con el despliegue, revisa que:
- El repositorio sea **Public**
- Los nombres de archivos sean exactos (sensible a mayúsculas)
- `requirements.txt` esté en la raíz del repo
