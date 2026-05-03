# 📊 TAV3-ST-QQE PRO v3 — Multi-Instrument

App web profesional **estilo TradingView** con triple confirmación.
**Forex completo + Metales preciosos + Crypto + Índices + Commodities.**

## ✨ Novedades v3

- 🌍 **+90 instrumentos**: 9 metales preciosos, 7 mayores Forex, 19 cruces, 17 exóticos, 7 crypto, 7 índices, 6 commodities
- 📊 **6 tipos de gráfico**: Velas, Heikin Ashi, Línea, Área, OHLC Bars, Velas huecas
- 🎯 **Señales en TF maestro (3M default), proyectadas al TF que estés viendo (1M, 5M, etc.)**
  - El TF de señales y el TF visible son INDEPENDIENTES
  - Pones gráfico en 1M, las señales se calculan en 3M y aparecen sobre tu gráfico de 1M
- 📊 **Volumen** opcional como subplot adicional
- 🎨 Bollinger + EMA20 + EMA100 con colores muy distintos
- 📉 Estocástico con sobrecompra/sobreventa sombreado
- 🔔 Sonido de campana en cada señal nueva
- 🌐 Sesiones: Sídney, Tokio, Londres, Nueva York
- 🪙 Crypto = mercado siempre abierto (sin "MERCADO CERRADO")

## 🎯 Lógica de timeframes

| Configuración | Comportamiento |
|--------------|----------------|
| Vista: **1M** + Señales: **3M** | Ves velas de 1M, las flechas BUY/SELL se calculan en 3M |
| Vista: **3M** + Señales: **3M** | Modo clásico, todo en 3M |
| Vista: **5M** + Señales: **3M** | Ves velas de 5M, señales más sensibles del 3M |
| Vista: **1H** + Señales: **15M** | Análisis de macro tendencia con señales del 15M |

**Tu setup recomendado:** Vista 1M + Señales 3M → operas en 1M con señales ya filtradas del 3M.

## 🚀 Despliegue Streamlit Cloud (10 min)

### 1) GitHub
- Crear cuenta: https://github.com/signup
- Nuevo repo público: https://github.com/new
- Nombre: `tav3-pro-app`

### 2) Subir archivos del ZIP
- `app.py`
- `requirements.txt`
- `README.md`
- `.streamlit/config.toml`

### 3) Desplegar
- https://share.streamlit.io
- New app → tu repo → `app.py` → Deploy

URL final: `https://tav3-pro-app-tu-usuario.streamlit.app`

## 🎨 Indicadores visuales

| Indicador | Color | Línea |
|-----------|-------|-------|
| Velas | Verde/Rojo TV | Normal |
| Bollinger | Naranja `#FFA726` | Gruesas |
| EMA 20 | Cyan `#00E5FF` | Gruesa 2.5 |
| EMA 100 | Magenta `#E040FB` | Gruesa 2.5 |
| Supertrend | Verde brillante / Rojo brillante | Gruesa 2.5 |
| Nube A-V2 | Verde translúcido | Relleno |
| ADX | Dorado `#FFD700` | Subplot |
| DI+/DI- | Verde / Rojo | Subplot |
| Estocástico | Azul / Naranja | Subplot |

## 🎮 Controles

- 🔍 Zoom: rueda ratón / pinch
- ✋ Pan: arrastrar
- ✏️ Dibujar: línea, rectángulo, círculo, lápiz, path
- 📷 Descargar PNG: 1800×900px
- 🎯 Crosshair: hover

## ⚠️ Limitaciones

- **Yahoo Finance**: delay ~15min, gratis pero no real-time
- **Forex exóticos**: algunos no tienen datos intraday en 1m, usar 5m+
- **Crypto**: 24/7 sin restricciones de fin de semana
- **Auto-refresh**: 30s

## 🧠 Lógica de señal

Una flecha BUY/SELL aparece SOLO cuando se cumplen TODAS en el TF maestro:

1. ✅ A-V2 alineado (Heikin Ashi suavizado)
2. ✅ Supertrend alineado
3. ✅ QQE Mod confirmando
4. ✅ Tendencia diaria a favor (o lateral si filtro está OFF)
5. ✅ ADX ≥ umbral (default 20)

Si una sola falta → no aparece la flecha. La señal del TF maestro luego se proyecta al TF visible para tu entrada precisa.
