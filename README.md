# 📊 TAV3-ST-QQE PRO v4

App web profesional con menú principal y soportes/resistencias automáticos.

## ✨ Novedades v4

- 🎛️ **Menú principal arriba**: Categoría, Instrumento, Tipo de gráfico, Temporalidad, TF señales en una sola fila
- 🧱 **Pisos y Techos automáticos del día** (Soportes y Resistencias):
  - Detecta pivots high/low en las velas del día
  - Agrupa pivots cercanos en niveles fuertes
  - Las líneas más fuertes (≥2 toques) salen sólidas y gruesas
  - Etiquetas a la derecha con precio + número de toques
  - Verde para pisos, rojo para techos
- 📊 Tabla con todos los niveles, sus toques y distancia % al precio actual
- ⚙️ Sidebar simplificado: solo parámetros avanzados

## 🎛️ Menú principal (arriba del gráfico)

```
[Categoría] [Instrumento] [Tipo gráfico] [Temporalidad] [Señales en]
```

5 selectboxes en una sola fila. Sin sidebar para lo básico — todo a mano.

## 🧱 Cómo funcionan los Pisos / Techos

Los pisos y techos se detectan con **pivots fractales**:
- Un **pivot high** = vela cuyo HIGH es mayor que las N velas a su izquierda Y derecha (default N=5)
- Un **pivot low** = vela cuyo LOW es menor que las N velas a su izquierda Y derecha
- Pivots dentro de una **tolerancia de 0.15%** se agrupan en un mismo nivel
- Cuantos más pivots toquen el mismo nivel = más fuerte (más toques)

**Visualización en el gráfico:**
- Línea **sólida y gruesa** = nivel fuerte (≥ N toques que configures)
- Línea **discontinua y fina** = pivot único, posible nivel naciente
- **Verde = piso (soporte)**, **Rojo = techo (resistencia)**
- Etiqueta a la derecha: `R 2,485.30 · 3x` (precio + número de toques)

**Configurable en sidebar:**
- Sensibilidad pivots (3-15): menor = más niveles, mayor = solo los más fuertes
- Máx niveles a mostrar (2-10)
- Toques mínimos para considerar "fuerte" (1-4)

## 📈 Cómo usarlos para tradear

- **Comprar cerca de soportes** (líneas verdes) cuando el precio rebota
- **Vender cerca de resistencias** (líneas rojas) cuando el precio se frena
- Si una resistencia **rompe**, se convierte en soporte (y viceversa)
- Los niveles **con más toques** son los más respetados por el mercado
- Las señales BUY/SELL del indicador combinadas con bounce desde soporte = setup A+

## 🌍 Instrumentos

| Categoría | Cantidad |
|-----------|----------|
| 🥇 Metales preciosos | 9 |
| 💱 Forex Mayores | 7 |
| 💱 Forex Cruces | 19 |
| 💱 Forex Exóticos | 17 |
| ₿ Crypto | 7 |
| 📊 Índices (S&P 500, US30, Nasdaq, Russell, DAX, FTSE, Nikkei, Hang Seng, VIX) | 12 |
| 🛢️ Commodities | 6 |
| **TOTAL** | **77 instrumentos** |

## 🎨 Tipos de gráfico

🕯️ Velas · 🟩 Heikin Ashi · 📉 Línea · 🌊 Área · 📊 OHLC Bars · ⬜ Velas huecas

## ⏱️ Doble timeframe

- **Vista**: lo que ves (1m, 3m, 5m, 15m, 30m, 1h, 4h, 1D)
- **Señales**: TF maestro donde se calculan las flechas (default 3m)

Tu setup recomendado: **Vista 1m + Señales 3m** → operar en 1m con señales filtradas del 3m.

## 🚀 Despliegue Streamlit Cloud (gratis)

1. Sube el ZIP a GitHub (`tav3-pro-app`)
2. https://share.streamlit.io → New app → tu repo → `app.py` → Deploy
3. URL: `https://tav3-pro-app-tu-usuario.streamlit.app`

Si ya la tienes desplegada: solo reemplaza `app.py` en GitHub y se redespliega.

## 🎮 Controles del gráfico

- 🔍 Zoom (rueda mouse)
- ✋ Pan (arrastrar)
- ✏️ Línea, rectángulo, círculo, lápiz, path
- 📷 Descargar PNG (1800×900)
- 🎯 Crosshair al hover
