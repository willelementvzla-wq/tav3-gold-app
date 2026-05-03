# 🥇 TAV3-ST-QQE GOLD PRO v2

App web profesional **estilo TradingView** para análisis del Oro (XAU/USD).

## ✨ Novedades v2

- 🎨 **Estilo TradingView**: paleta `#131722`, fuentes pequeñas, layout compacto sin espacios desperdiciados
- 📊 **Bollinger Bands** (naranja) + **EMA 20** (cyan) + **EMA 100** (magenta) — colores muy distintos, líneas gruesas
- 🌍 **Sesiones de mercado** con sombreado y barra de estado:
  - 🟠 Sídney
  - 🟡 Tokio
  - 🔵 Londres
  - 🟣 Nueva York
- 🔔 **Sonido de campana** con cada señal nueva (Web Audio API, sin archivos externos)
- 📉 **Estocástico** con zonas de sobrecompra (>80) y sobreventa (<20) sombreadas
- ⚡ **Auto-refresh cada 30 segundos** mientras el mercado esté abierto
- 🔴 Indicador "MERCADO CERRADO" automático fuera de horario (sáb 22:00 UTC viernes hasta dom 22:00 UTC)
- 📊 Spike lines tipo TradingView al pasar el mouse

## 🚀 Despliegue gratis en Streamlit Cloud (10 min)

### 1) Crear cuenta GitHub
https://github.com/signup (gratis)

### 2) Nuevo repositorio público
- https://github.com/new
- Nombre: `tav3-gold-app`
- Public ✅
- Create repository

### 3) Subir archivos
1. Click "uploading an existing file"
2. Sube: `app.py`, `requirements.txt`, `README.md`
3. Para `.streamlit/config.toml`:
   - Click "Add file" → "Create new file"
   - Nombre: `.streamlit/config.toml`
   - Pega contenido del config
4. Commit changes

### 4) Desplegar
1. https://share.streamlit.io
2. Login con GitHub
3. New app → tu repo → `app.py` → Deploy

✅ **Listo. URL:** `https://tav3-gold-app-tu-usuario.streamlit.app`

## 🎮 Controles del gráfico

- 🔍 **Zoom**: rueda del mouse / pellizco táctil
- ✋ **Pan**: arrastrar
- ✏️ **Dibujar**: línea / rectángulo / círculo / lápiz / path / borrador (barra superior)
- 📷 **Descargar PNG**: botón de cámara
- 🎯 **Crosshair**: aparece automático al hover

## 📈 Indicadores integrados

| Indicador | Color | Uso |
|-----------|-------|-----|
| Velas precio | Verde/Rojo TradingView | Acción del precio |
| Bollinger Bands | Naranja `#FFA726` | Volatilidad y rangos |
| EMA 20 | Cyan `#00E5FF` | Tendencia corto plazo |
| EMA 100 | Magenta `#E040FB` | Tendencia medio plazo |
| Supertrend | Verde/Rojo brillante | Cambios de tendencia |
| Nube A-V2 | Verde/Rojo translúcido | Filtro Heikin Ashi |
| ADX + DI± | Dorado / Verde / Rojo | Fuerza tendencia |
| Estocástico %K %D | Azul / Naranja | Sobrecompra/Sobreventa |

## 🔊 Sonidos

Cada nueva señal BUY/SELL reproduce **doble campana** generada por Web Audio API:
- 880Hz → 1320Hz → 880Hz
- Solo suena UNA vez por señal (controlado en sesión)
- Activable/desactivable desde sidebar

## ⚠️ Limitaciones

- **Yahoo Finance**: delay ~15 min (gratis). Para datos en tiempo real real-time se necesita broker API.
- **Auto-refresh**: cada 30s. Si abres la pestaña en otro lado, se actualiza al volver.
- **Mercado cerrado**: durante fines de semana (sáb 22:00 UTC viernes — dom 22:00 UTC) los datos no avanzan, pero la app sigue funcional para análisis histórico.

## 🧠 Lógica de señal

Una flecha BUY/SELL aparece SOLO cuando se cumplen TODAS:
1. ✅ A-V2 alineado
2. ✅ Supertrend alineado
3. ✅ QQE Mod confirmando
4. ✅ Tendencia diaria a favor (o lateral si filtro está OFF)
5. ✅ ADX ≥ umbral (default 20)

Si una sola falta, no aparece la flecha. Esto reduce falsos positivos drásticamente.
