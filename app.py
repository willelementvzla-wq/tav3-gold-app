"""
TAV3-ST-QQE GOLD - Triple Confirmation Pro
App web con Streamlit para analisis del Oro (XAU/USD)
Datos 100% reales via Yahoo Finance
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="TAV3 GOLD Pro",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { padding-top: 0.5rem; }
    .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 100%; }
    [data-testid="stMetricValue"] { font-size: 1.1rem; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; color: #888; }
    .stAlert { padding: 0.5rem 1rem; }
    h1 { font-size: 1.8rem !important; padding-bottom: 0.3rem; }
    h2 { font-size: 1.3rem !important; padding-top: 0.5rem; padding-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("⚙️ Configuración")

    sym_options = {
        "GC=F (Gold Futures COMEX)": "GC=F",
        "XAUUSD=X (Spot Gold)": "XAUUSD=X",
        "GLD (ETF SPDR Gold)": "GLD",
    }
    sym_label = st.selectbox("Símbolo", list(sym_options.keys()), index=0)
    sym_code = sym_options[sym_label]

    tf_options = {
        "1 minuto": (1, "5d"),
        "3 minutos ⭐": (3, "5d"),
        "5 minutos": (5, "30d"),
        "15 minutos": (15, "60d"),
        "30 minutos": (30, "60d"),
        "1 hora": (60, "180d"),
        "4 horas": (240, "365d"),
        "1 día": (1440, "730d"),
    }
    tf_label = st.selectbox("Temporalidad", list(tf_options.keys()), index=1)
    tf_minutes, period = tf_options[tf_label]

    candles_to_show = st.slider("Velas a mostrar", 50, 500, 200, 25)

    st.divider()
    st.subheader("Parámetros")
    ma_period = st.slider("MA Period (A-V2)", 10, 100, 52)
    ma_smooth = st.slider("MA Smoothing", 5, 30, 10)
    st_period = st.slider("ATR Period (Supertrend)", 5, 20, 10)
    st_mult = st.slider("ATR Multiplier", 1.0, 5.0, 3.0, 0.1)
    adx_threshold = st.slider("ADX umbral fuerza", 15, 35, 20)
    use_daily = st.checkbox("Filtro tendencia diaria", value=True)
    show_st_lines = st.checkbox("Líneas Supertrend", value=True)
    show_signals = st.checkbox("Señales BUY/SELL", value=True)

    st.divider()
    if st.button("🔄 Actualizar datos", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"⏱️ Última actualización: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# DATA FETCH (100% real desde Yahoo Finance)
# ============================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_data(symbol, period, interval):
    df = yf.download(symbol, period=period, interval=interval,
                      progress=False, auto_adjust=False, prepost=False)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    return df

def get_data(sym, tf_min, period):
    """Yahoo soporta: 1m, 2m, 5m, 15m, 30m, 60m/1h, 1d
       Para 3m y 4h hacemos resample"""
    try:
        if tf_min == 1:
            return fetch_data(sym, period, "1m")
        elif tf_min == 3:
            df1 = fetch_data(sym, period, "1m")
            return df1.resample('3min').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min',
                'Close': 'last', 'Volume': 'sum'}).dropna()
        elif tf_min in (5, 15, 30):
            return fetch_data(sym, period, f"{tf_min}m")
        elif tf_min == 60:
            return fetch_data(sym, period, "1h")
        elif tf_min == 240:
            df1 = fetch_data(sym, period, "1h")
            return df1.resample('4h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min',
                'Close': 'last', 'Volume': 'sum'}).dropna()
        else:
            return fetch_data(sym, period, "1d")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

# ============================================================
# INDICADORES (port fiel del Pine Script)
# ============================================================
def heikin_ashi(df):
    ha = pd.DataFrame(index=df.index)
    ha['close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    ha['open'] = 0.0
    open_arr = np.zeros(len(df))
    open_arr[0] = (df['Open'].iloc[0] + df['Close'].iloc[0]) / 2
    close_arr = ha['close'].values
    for i in range(1, len(df)):
        open_arr[i] = (open_arr[i-1] + close_arr[i-1]) / 2
    ha['open'] = open_arr
    ha['high'] = pd.concat([ha['close'], ha['open'], df['High']], axis=1).max(axis=1)
    ha['low']  = pd.concat([ha['close'], ha['open'], df['Low']],  axis=1).min(axis=1)
    return ha

def vwma(price, volume, length):
    vol = volume.replace(0, np.nan).ffill().fillna(1)
    if vol.sum() == 0 or vol.isna().all():
        return price.ewm(span=length, adjust=False).mean()
    return (price * vol).rolling(length, min_periods=1).sum() / vol.rolling(length, min_periods=1).sum()

def supertrend(df, period, multiplier):
    high, low, close = df['High'].values, df['Low'].values, df['Close'].values
    n = len(df)
    hl2 = (high + low) / 2

    # ATR (Wilder)
    tr = np.zeros(n)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1]))
    atr = np.zeros(n)
    atr[0] = tr[0]
    alpha = 1 / period
    for i in range(1, n):
        atr[i] = atr[i-1] * (1 - alpha) + tr[i] * alpha

    upperband = hl2 - multiplier * atr
    lowerband = hl2 + multiplier * atr
    upper = np.copy(upperband)
    lower = np.copy(lowerband)
    trend = np.ones(n, dtype=int)

    for i in range(1, n):
        upper[i] = max(upperband[i], upper[i-1]) if close[i-1] > upper[i-1] else upperband[i]
        lower[i] = min(lowerband[i], lower[i-1]) if close[i-1] < lower[i-1] else lowerband[i]
        if trend[i-1] == -1 and close[i] > lower[i-1]:
            trend[i] = 1
        elif trend[i-1] == 1 and close[i] < upper[i-1]:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

    return pd.Series(trend, index=df.index), pd.Series(upper, index=df.index), pd.Series(lower, index=df.index)

def rsi(close, period):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))

def qqe_mod(close, rsi_period=6, sf=5, qqe_factor=3.0,
            bb_length=50, bb_mult=0.35,
            rsi_period2=6, sf2=5, threshhold2=3):
    """Port del QQE Mod de Mihkel00"""
    n = len(close)
    wilders = rsi_period * 2 - 1
    rsi_v = rsi(close, rsi_period)
    rsi_ma = rsi_v.ewm(span=sf, adjust=False).mean()
    atr_rsi = (rsi_ma.shift() - rsi_ma).abs()
    ma_atr = atr_rsi.ewm(span=wilders, adjust=False).mean()
    dar = ma_atr.ewm(span=wilders, adjust=False).mean() * qqe_factor

    rsi_ma_v = rsi_ma.values
    dar_v = dar.values
    longband = np.zeros(n)
    shortband = np.zeros(n)
    trend_q = np.zeros(n, dtype=int)

    for i in range(1, n):
        if np.isnan(dar_v[i]):
            longband[i] = longband[i-1]
            shortband[i] = shortband[i-1]
            trend_q[i] = trend_q[i-1]
            continue
        new_short = rsi_ma_v[i] + dar_v[i]
        new_long = rsi_ma_v[i] - dar_v[i]
        if rsi_ma_v[i-1] > longband[i-1] and rsi_ma_v[i] > longband[i-1]:
            longband[i] = max(longband[i-1], new_long)
        else:
            longband[i] = new_long
        if rsi_ma_v[i-1] < shortband[i-1] and rsi_ma_v[i] < shortband[i-1]:
            shortband[i] = min(shortband[i-1], new_short)
        else:
            shortband[i] = new_short
        if rsi_ma_v[i] > shortband[i-1] and rsi_ma_v[i-1] <= shortband[i-1]:
            trend_q[i] = 1
        elif rsi_ma_v[i-1] >= longband[i-1] and rsi_ma_v[i] < longband[i-1]:
            trend_q[i] = -1
        else:
            trend_q[i] = trend_q[i-1]

    fast_atr_rsi_tl = pd.Series(np.where(trend_q == 1, longband, shortband), index=close.index)
    basis = (fast_atr_rsi_tl - 50).rolling(bb_length, min_periods=1).mean()
    dev = bb_mult * (fast_atr_rsi_tl - 50).rolling(bb_length, min_periods=1).std()
    upper_b = basis + dev
    lower_b = basis - dev

    rsi_v2 = rsi(close, rsi_period2)
    rsi_ma2 = rsi_v2.ewm(span=sf2, adjust=False).mean()

    blue_bar = ((rsi_ma2 - 50) > threshhold2) & ((rsi_ma - 50) > upper_b)
    red_bar = ((rsi_ma2 - 50) < -threshhold2) & ((rsi_ma - 50) < lower_b)

    return blue_bar.fillna(False), red_bar.fillna(False), rsi_ma, rsi_ma2

def adx_dmi(df, period=14):
    high, low, close = df['High'], df['Low'], df['Close']
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    mask = plus_dm > minus_dm
    plus_dm = plus_dm.where(mask, 0)
    minus_dm = minus_dm.where(~mask, 0)

    tr = pd.concat([high - low,
                    (high - close.shift()).abs(),
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-10)
    adx_v = dx.ewm(alpha=1/period, adjust=False).mean()
    return adx_v, plus_di, minus_di

def daily_trend(df_d, fast=20, slow=50):
    if len(df_d) < slow + 5:
        return 0, 0
    ema_f = df_d['Close'].ewm(span=fast, adjust=False).mean()
    ema_s = df_d['Close'].ewm(span=slow, adjust=False).mean()
    last_close = df_d['Close'].iloc[-1]
    last_open = df_d['Open'].iloc[-1]
    if ema_f.iloc[-1] > ema_s.iloc[-1] and last_close > ema_f.iloc[-1]:
        trend = 1
    elif ema_f.iloc[-1] < ema_s.iloc[-1] and last_close < ema_f.iloc[-1]:
        trend = -1
    else:
        trend = 0
    pct_change = ((last_close - last_open) / last_open) * 100
    return trend, pct_change

# ============================================================
# CARGAR DATOS
# ============================================================
with st.spinner("📡 Descargando datos del oro en tiempo real..."):
    df = get_data(sym_code, tf_minutes, period)
    df_daily = fetch_data(sym_code, "180d", "1d")

if df.empty or len(df) < 100:
    st.error("❌ No se pudieron cargar suficientes datos. Intenta otra temporalidad o más tarde.")
    st.stop()

# ============================================================
# CALCULAR INDICADORES
# ============================================================
ha = heikin_ashi(df)
ha_o_ma = vwma(ha['open'], df['Volume'], ma_period)
ha_c_ma = vwma(ha['close'], df['Volume'], ma_period)
ha_h_ma = vwma(ha['high'], df['Volume'], ma_period)
ha_l_ma = vwma(ha['low'], df['Volume'], ma_period)
ha_o_smooth = vwma(ha_o_ma, df['Volume'], ma_smooth)
ha_c_smooth = vwma(ha_c_ma, df['Volume'], ma_smooth)
ha_h_smooth = vwma(ha_h_ma, df['Volume'], ma_smooth)
ha_l_smooth = vwma(ha_l_ma, df['Volume'], ma_smooth)
av2_bull = ha_c_smooth >= ha_o_smooth

trend_st, st_upper, st_lower = supertrend(df, st_period, st_mult)
blue_bar, red_bar, rsi_ma, rsi_ma2 = qqe_mod(df['Close'])
adx_v, plus_di, minus_di = adx_dmi(df, 14)
strong = adx_v >= adx_threshold

d_trend, d_change = daily_trend(df_daily, 20, 50)
ok_long = (not use_daily) or (d_trend >= 0)
ok_short = (not use_daily) or (d_trend <= 0)

long_sig = av2_bull & (trend_st == 1) & blue_bar & strong & ok_long
short_sig = (~av2_bull) & (trend_st == -1) & red_bar & strong & ok_short

long_cond = long_sig & (~long_sig.shift(1).fillna(False))
short_cond = short_sig & (~short_sig.shift(1).fillna(False))

# ============================================================
# HEADER + KPIs
# ============================================================
last_price = df['Close'].iloc[-1]
prev_price = df['Close'].iloc[-2]
price_change = ((last_price - prev_price) / prev_price) * 100

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title(f"🥇 {sym_label.split(' ')[0]} • {tf_label}")
with col_t2:
    st.metric("Precio actual", f"${last_price:,.2f}", f"{price_change:+.3f}%")

# Panel de fuerza
col1, col2, col3, col4, col5, col6 = st.columns(6)

d_label = "🟢 ALCISTA" if d_trend == 1 else "🔴 BAJISTA" if d_trend == -1 else "🟡 LATERAL"
col1.metric("📅 Tendencia Diaria", d_label, f"{d_change:+.2f}% hoy")

adx_now = float(adx_v.iloc[-1]) if not pd.isna(adx_v.iloc[-1]) else 0
adx_status = "💪 FUERTE" if adx_now >= adx_threshold else "😴 DÉBIL"
col2.metric("⚡ ADX", f"{adx_now:.1f}", adx_status)

av2_label = "🟢 ALCISTA" if av2_bull.iloc[-1] else "🔴 BAJISTA"
col3.metric("📈 A-V2", av2_label)

st_label = "🟢 ALCISTA" if trend_st.iloc[-1] == 1 else "🔴 BAJISTA"
col4.metric("📊 Supertrend", st_label)

qqe_label = "🔵 COMPRA" if blue_bar.iloc[-1] else "🔴 VENTA" if red_bar.iloc[-1] else "⚪ NEUTRAL"
col5.metric("🎯 QQE", qqe_label)

# Score total
score_l = sum([
    20 if av2_bull.iloc[-1] else 0,
    20 if trend_st.iloc[-1] == 1 else 0,
    20 if blue_bar.iloc[-1] else 0,
    20 if d_trend == 1 else 0,
    20 if (strong.iloc[-1] and plus_di.iloc[-1] > minus_di.iloc[-1]) else 0,
])
score_s = sum([
    20 if not av2_bull.iloc[-1] else 0,
    20 if trend_st.iloc[-1] == -1 else 0,
    20 if red_bar.iloc[-1] else 0,
    20 if d_trend == -1 else 0,
    20 if (strong.iloc[-1] and minus_di.iloc[-1] > plus_di.iloc[-1]) else 0,
])
final_score = max(score_l, score_s)
direction = "🟢 LARGO" if score_l >= score_s else "🔴 CORTO"
score_emoji = "✅" if final_score >= 80 else "⚠️" if final_score >= 60 else "❌"
col6.metric("💪 FUERZA TOTAL", f"{score_emoji} {final_score}%", direction)

# Recomendación
if final_score >= 80:
    st.success(f"✅ **OPERAR {direction}** - Triple confirmación + tendencia diaria a favor + ADX fuerte")
elif final_score >= 60:
    st.warning(f"⚠️ **ESPERAR mejor entrada** - Confirmación parcial ({final_score}%)")
else:
    st.error(f"❌ **NO OPERAR** - Sin confirmación clara ({final_score}%)")

# ============================================================
# GRÁFICO PRINCIPAL CON PLOTLY (zoom, dibujo, etc.)
# ============================================================
df_show = df.tail(candles_to_show).copy()
ha_o_s = ha_o_smooth.tail(candles_to_show)
ha_c_s = ha_c_smooth.tail(candles_to_show)
ha_h_s = ha_h_smooth.tail(candles_to_show)
ha_l_s = ha_l_smooth.tail(candles_to_show)
trend_st_s = trend_st.tail(candles_to_show)
st_upper_s = st_upper.tail(candles_to_show)
st_lower_s = st_lower.tail(candles_to_show)
adx_s = adx_v.tail(candles_to_show)
plus_di_s = plus_di.tail(candles_to_show)
minus_di_s = minus_di.tail(candles_to_show)
long_cond_s = long_cond.tail(candles_to_show)
short_cond_s = short_cond.tail(candles_to_show)

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.75, 0.25],
    subplot_titles=("", "ADX & DMI")
)

# Velas reales
fig.add_trace(go.Candlestick(
    x=df_show.index,
    open=df_show['Open'], high=df_show['High'],
    low=df_show['Low'], close=df_show['Close'],
    name='Precio',
    increasing_line_color='#26A69A',
    decreasing_line_color='#EF5350',
    increasing_fillcolor='#26A69A',
    decreasing_fillcolor='#EF5350',
), row=1, col=1)

# Nube A-V2
trend_color = ['rgba(38,166,154,0.3)' if c >= o else 'rgba(239,83,80,0.3)'
               for c, o in zip(ha_c_s, ha_o_s)]
fig.add_trace(go.Scatter(x=ha_c_s.index, y=ha_o_s, mode='lines',
                          line=dict(color='rgba(0,0,0,0)', width=0),
                          showlegend=False, hoverinfo='skip'), row=1, col=1)
fig.add_trace(go.Scatter(x=ha_c_s.index, y=ha_c_s, mode='lines',
                          line=dict(color='rgba(0,0,0,0)', width=0),
                          fill='tonexty', fillcolor='rgba(38,166,154,0.15)',
                          name='A-V2 Cloud', hoverinfo='skip'), row=1, col=1)

fig.add_trace(go.Scatter(x=ha_h_s.index, y=ha_h_s, mode='lines',
                          line=dict(color='gray', width=1, dash='dot'),
                          name='HA High smooth', opacity=0.5), row=1, col=1)
fig.add_trace(go.Scatter(x=ha_l_s.index, y=ha_l_s, mode='lines',
                          line=dict(color='gray', width=1, dash='dot'),
                          name='HA Low smooth', opacity=0.5), row=1, col=1)

# Supertrend
if show_st_lines:
    st_up_plot = st_upper_s.where(trend_st_s == 1)
    st_dn_plot = st_lower_s.where(trend_st_s == -1)
    fig.add_trace(go.Scatter(x=st_up_plot.index, y=st_up_plot, mode='lines',
                              line=dict(color='#00ff00', width=2),
                              name='Supertrend Up'), row=1, col=1)
    fig.add_trace(go.Scatter(x=st_dn_plot.index, y=st_dn_plot, mode='lines',
                              line=dict(color='#ff0000', width=2),
                              name='Supertrend Down'), row=1, col=1)

# Señales BUY/SELL
if show_signals:
    buy_pts = df_show[long_cond_s]
    sell_pts = df_show[short_cond_s]
    if not buy_pts.empty:
        fig.add_trace(go.Scatter(
            x=buy_pts.index, y=buy_pts['Low'] * 0.999,
            mode='markers+text', text=['BUY'] * len(buy_pts),
            textposition='bottom center',
            textfont=dict(color='lime', size=11, family='Arial Black'),
            marker=dict(symbol='triangle-up', size=14, color='lime',
                        line=dict(color='white', width=1)),
            name='BUY signal'), row=1, col=1)
    if not sell_pts.empty:
        fig.add_trace(go.Scatter(
            x=sell_pts.index, y=sell_pts['High'] * 1.001,
            mode='markers+text', text=['SELL'] * len(sell_pts),
            textposition='top center',
            textfont=dict(color='red', size=11, family='Arial Black'),
            marker=dict(symbol='triangle-down', size=14, color='red',
                        line=dict(color='white', width=1)),
            name='SELL signal'), row=1, col=1)

# ADX subplot
fig.add_trace(go.Scatter(x=adx_s.index, y=adx_s, mode='lines',
                          line=dict(color='#FFD700', width=2),
                          name='ADX'), row=2, col=1)
fig.add_trace(go.Scatter(x=plus_di_s.index, y=plus_di_s, mode='lines',
                          line=dict(color='#26A69A', width=1.5),
                          name='DI+'), row=2, col=1)
fig.add_trace(go.Scatter(x=minus_di_s.index, y=minus_di_s, mode='lines',
                          line=dict(color='#EF5350', width=1.5),
                          name='DI-'), row=2, col=1)
fig.add_hline(y=adx_threshold, line=dict(color='white', width=1, dash='dash'),
              row=2, col=1)

# Layout con HERRAMIENTAS DE DIBUJO
fig.update_layout(
    template='plotly_dark',
    height=750,
    margin=dict(l=10, r=10, t=30, b=10),
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
    xaxis_rangeslider_visible=False,
    dragmode='pan',  # Por defecto pan; puede cambiar a drawing en modebar
    newshape=dict(line=dict(color='cyan', width=2)),
    hovermode='x unified',
)

# Ocultar gaps (fines de semana, horas no trading)
fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])] if tf_minutes < 1440 else [])

# Configuración de modebar con TODAS las herramientas de dibujo
config = {
    'scrollZoom': True,
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': [
        'drawline', 'drawopenpath', 'drawclosedpath',
        'drawcircle', 'drawrect', 'eraseshape'
    ],
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': f'TAV3_GOLD_{tf_label}',
        'height': 800, 'width': 1600, 'scale': 2
    }
}

st.plotly_chart(fig, use_container_width=True, config=config)

# ============================================================
# TABLA DE SEÑALES RECIENTES
# ============================================================
with st.expander("📋 Últimas señales detectadas", expanded=False):
    signals = []
    for idx in df.index[long_cond]:
        signals.append({
            'Fecha/Hora': idx,
            'Tipo': '🟢 BUY',
            'Precio': df.loc[idx, 'Close'],
            'ADX': adx_v.loc[idx] if idx in adx_v.index else None,
        })
    for idx in df.index[short_cond]:
        signals.append({
            'Fecha/Hora': idx,
            'Tipo': '🔴 SELL',
            'Precio': df.loc[idx, 'Close'],
            'ADX': adx_v.loc[idx] if idx in adx_v.index else None,
        })
    if signals:
        df_sig = pd.DataFrame(signals).sort_values('Fecha/Hora', ascending=False).head(20)
        df_sig['ADX'] = df_sig['ADX'].apply(lambda x: f"{x:.1f}" if x else "-")
        df_sig['Precio'] = df_sig['Precio'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_sig, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay señales en este rango de datos.")

# Footer
st.caption("📊 Datos en tiempo real desde Yahoo Finance · Actualización automática cada 60s · "
           "Herramientas de dibujo: usa los iconos en la barra superior del gráfico (línea, rectángulo, círculo, lápiz, borrador) · "
           "Zoom: rueda del mouse o click+arrastrar")
