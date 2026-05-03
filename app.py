"""
TAV3-ST-QQE PRO v3 — Multi-instrument trading dashboard
- Todos los pares Forex + metales preciosos + crypto
- Tipos de gráfico: Velas, Heikin Ashi, Línea, Área, OHLC, Hollow candles
- Señales calculadas en 3M, proyectadas al timeframe que estés viendo
- Sesiones, sonido, Bollinger, EMAs, Estocástico, ADX
"""
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="TAV3 PRO Multi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS estilo TradingView, compacto
st.markdown("""
<style>
    .main { padding: 0rem !important; }
    .block-container {
        padding: 0.3rem 0.6rem 0rem 0.6rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] { height: 0px; display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    [data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.65rem !important; color: #787b86 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }

    section[data-testid="stSidebar"] > div { padding-top: 1rem; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stCheckbox label {
        font-size: 0.75rem !important;
    }

    h1 { font-size: 1.1rem !important; padding: 0 !important; margin: 0.2rem 0 !important; color: #d1d4dc; font-weight: 600; }
    h2 { font-size: 0.95rem !important; padding: 0 !important; margin: 0.2rem 0 !important; }
    h3 { font-size: 0.85rem !important; padding: 0 !important; margin: 0.2rem 0 !important; }

    .stAlert { padding: 0.3rem 0.7rem !important; font-size: 0.8rem !important; }
    .stApp { background-color: #131722; }
    .streamlit-expanderHeader { font-size: 0.8rem !important; padding: 0.3rem !important; }
    [data-testid="stDataFrame"] { font-size: 0.75rem; }
    div[data-testid="column"] { padding: 0.1rem 0.2rem !important; }

    .status-bar {
        background: #1e222d;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        border: 1px solid #2a2e39;
        font-size: 0.75rem;
        color: #d1d4dc;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .session-active {
        color: white; padding: 2px 8px; border-radius: 3px;
        font-weight: 600; font-size: 0.7rem;
    }
    .session-closed {
        background: #363a45; color: #787b86;
        padding: 2px 8px; border-radius: 3px; font-size: 0.7rem;
    }

    /* Banner de señal en TF actual basada en 3M */
    .signal-banner {
        background: linear-gradient(90deg, #00E676 0%, #00C853 100%);
        color: #000; padding: 8px 16px; border-radius: 4px;
        font-weight: bold; text-align: center; font-size: 0.9rem;
        margin: 4px 0;
    }
    .signal-banner-sell {
        background: linear-gradient(90deg, #FF1744 0%, #D50000 100%);
        color: white; padding: 8px 16px; border-radius: 4px;
        font-weight: bold; text-align: center; font-size: 0.9rem;
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh 30s
components.html("""
<script>
    setTimeout(function(){ window.parent.location.reload(); }, 30000);
</script>
""", height=0)

# ============================================================
# CATÁLOGO COMPLETO DE INSTRUMENTOS
# ============================================================
INSTRUMENTS = {
    "🥇 Metales preciosos": {
        "Oro Futures (GC=F)": "GC=F",
        "Oro Spot (XAUUSD)": "XAUUSD=X",
        "Plata Futures (SI=F)": "SI=F",
        "Plata Spot (XAGUSD)": "XAGUSD=X",
        "Platino Futures (PL=F)": "PL=F",
        "Paladio Futures (PA=F)": "PA=F",
        "Cobre Futures (HG=F)": "HG=F",
        "Oro ETF (GLD)": "GLD",
        "Plata ETF (SLV)": "SLV",
    },
    "💱 Forex Mayores": {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "USD/CHF": "CHF=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "CAD=X",
        "NZD/USD": "NZDUSD=X",
    },
    "💱 Forex Cruces": {
        "EUR/GBP": "EURGBP=X",
        "EUR/JPY": "EURJPY=X",
        "EUR/CHF": "EURCHF=X",
        "EUR/AUD": "EURAUD=X",
        "EUR/CAD": "EURCAD=X",
        "GBP/JPY": "GBPJPY=X",
        "GBP/CHF": "GBPCHF=X",
        "GBP/AUD": "GBPAUD=X",
        "GBP/CAD": "GBPCAD=X",
        "AUD/JPY": "AUDJPY=X",
        "AUD/CHF": "AUDCHF=X",
        "AUD/CAD": "AUDCAD=X",
        "AUD/NZD": "AUDNZD=X",
        "CAD/JPY": "CADJPY=X",
        "CAD/CHF": "CADCHF=X",
        "CHF/JPY": "CHFJPY=X",
        "NZD/JPY": "NZDJPY=X",
        "NZD/CAD": "NZDCAD=X",
        "NZD/CHF": "NZDCHF=X",
    },
    "💱 Forex Exóticos": {
        "USD/MXN": "MXN=X",
        "USD/ZAR": "ZAR=X",
        "USD/TRY": "TRY=X",
        "USD/BRL": "BRL=X",
        "USD/INR": "INR=X",
        "USD/CNY": "CNY=X",
        "USD/HKD": "HKD=X",
        "USD/SGD": "SGD=X",
        "USD/SEK": "SEK=X",
        "USD/NOK": "NOK=X",
        "USD/DKK": "DKK=X",
        "USD/PLN": "PLN=X",
        "USD/RUB": "RUB=X",
        "USD/THB": "THB=X",
        "USD/CLP": "CLP=X",
        "USD/COP": "COP=X",
        "USD/ARS": "ARS=X",
    },
    "₿ Crypto": {
        "Bitcoin (BTC-USD)": "BTC-USD",
        "Ethereum (ETH-USD)": "ETH-USD",
        "Solana (SOL-USD)": "SOL-USD",
        "BNB (BNB-USD)": "BNB-USD",
        "XRP (XRP-USD)": "XRP-USD",
        "Cardano (ADA-USD)": "ADA-USD",
        "Dogecoin (DOGE-USD)": "DOGE-USD",
    },
    "📊 Índices": {
        "S&P 500 (^GSPC)": "^GSPC",
        "Nasdaq (^IXIC)": "^IXIC",
        "Dow Jones (^DJI)": "^DJI",
        "DAX (^GDAXI)": "^GDAXI",
        "FTSE 100 (^FTSE)": "^FTSE",
        "Nikkei (^N225)": "^N225",
        "Hang Seng (^HSI)": "^HSI",
    },
    "🛢️ Commodities": {
        "Petróleo WTI (CL=F)": "CL=F",
        "Petróleo Brent (BZ=F)": "BZ=F",
        "Gas Natural (NG=F)": "NG=F",
        "Maíz (ZC=F)": "ZC=F",
        "Trigo (ZW=F)": "ZW=F",
        "Café (KC=F)": "KC=F",
    },
}

CHART_TYPES = [
    "🕯️ Velas",
    "🟩 Heikin Ashi",
    "📉 Línea",
    "🌊 Área",
    "📊 OHLC Bars",
    "⬜ Velas huecas",
]

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Config")

    # Categoría
    category = st.selectbox("Categoría", list(INSTRUMENTS.keys()), index=0)
    sym_label = st.selectbox("Instrumento", list(INSTRUMENTS[category].keys()), index=0)
    sym_code = INSTRUMENTS[category][sym_label]

    # Tipo de gráfico
    chart_type = st.selectbox("Tipo de gráfico", CHART_TYPES, index=0)

    # Temporalidad (visualización)
    tf_options = {
        "1m": (1, "5d"),
        "3m": (3, "5d"),
        "5m": (5, "30d"),
        "15m": (15, "60d"),
        "30m": (30, "60d"),
        "1h": (60, "180d"),
        "4h": (240, "365d"),
        "1D": (1440, "730d"),
    }
    tf_label = st.selectbox("⏱️ Temporalidad gráfico", list(tf_options.keys()), index=0,
                             help="Lo que ves en el gráfico. Las señales SIEMPRE se calculan en 3M.")
    tf_minutes, period = tf_options[tf_label]

    # TF de las señales (fijo en 3M, pero ajustable)
    signal_tf = st.selectbox("🎯 TF de señales (maestro)",
                              ["1m", "3m", "5m", "15m"], index=1,
                              help="Las señales BUY/SELL se calculan SIEMPRE en este timeframe, sin importar el TF que estés viendo.")
    sig_tf_min = {"1m": 1, "3m": 3, "5m": 5, "15m": 15}[signal_tf]

    candles_to_show = st.slider("Velas", 50, 500, 200, 25)

    st.markdown("##### 📊 Indicadores")
    show_bb = st.checkbox("Bollinger Bands", value=True)
    show_ema20 = st.checkbox("EMA 20", value=True)
    show_ema100 = st.checkbox("EMA 100", value=True)
    show_st_lines = st.checkbox("Supertrend", value=True)
    show_cloud = st.checkbox("Nube A-V2", value=True)
    show_signals = st.checkbox("Señales BUY/SELL", value=True)
    show_sessions = st.checkbox("Sesiones", value=True)
    show_volume = st.checkbox("Volumen", value=False)

    st.markdown("##### 🔧 Parámetros")
    ma_period = st.slider("MA A-V2", 10, 100, 52)
    ma_smooth = st.slider("MA Smooth", 5, 30, 10)
    st_period = st.slider("ATR Period", 5, 20, 10)
    st_mult = st.slider("ATR Mult", 1.0, 5.0, 3.0, 0.1)
    adx_threshold = st.slider("ADX umbral", 15, 35, 20)
    bb_period = st.slider("BB Period", 10, 50, 20)
    bb_std = st.slider("BB Std", 1.0, 3.0, 2.0, 0.1)
    stoch_k = st.slider("Stoch %K", 5, 30, 14)
    stoch_d = st.slider("Stoch %D", 1, 10, 3)

    use_daily = st.checkbox("Filtro tendencia diaria", value=True)
    sound_on = st.checkbox("🔔 Sonido en señales", value=True)

    st.divider()
    if st.button("🔄 Refresh", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# DATA FETCH
# ============================================================
@st.cache_data(ttl=30, show_spinner=False)
def fetch_data(symbol, period, interval):
    df = yf.download(symbol, period=period, interval=interval,
                     progress=False, auto_adjust=False, prepost=True)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    else:
        df.index = df.index.tz_convert('UTC')
    return df

def get_data(sym, tf_min, period):
    try:
        if tf_min == 1:
            return fetch_data(sym, period, "1m")
        elif tf_min == 3:
            df1 = fetch_data(sym, period, "1m")
            if df1.empty:
                return df1
            return df1.resample('3min').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min',
                'Close': 'last', 'Volume': 'sum'}).dropna()
        elif tf_min in (5, 15, 30):
            return fetch_data(sym, period, f"{tf_min}m")
        elif tf_min == 60:
            return fetch_data(sym, period, "1h")
        elif tf_min == 240:
            df1 = fetch_data(sym, period, "1h")
            if df1.empty:
                return df1
            return df1.resample('4h').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min',
                'Close': 'last', 'Volume': 'sum'}).dropna()
        else:
            return fetch_data(sym, period, "1d")
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ============================================================
# INDICADORES
# ============================================================
def heikin_ashi(df):
    ha = pd.DataFrame(index=df.index)
    ha['close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
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
    n = len(close)
    rsi_v = rsi(close, rsi_period)
    rsi_ma = rsi_v.ewm(span=sf, adjust=False).mean()
    atr_rsi = (rsi_ma.shift() - rsi_ma).abs()
    wilders = rsi_period * 2 - 1
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
    return blue_bar.fillna(False), red_bar.fillna(False)

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

def bollinger(close, period, std_mult):
    basis = close.rolling(period, min_periods=1).mean()
    dev = close.rolling(period, min_periods=1).std()
    upper = basis + std_mult * dev
    lower = basis - std_mult * dev
    return basis, upper, lower

def stochastic(df, k_period, d_period):
    low_min = df['Low'].rolling(k_period, min_periods=1).min()
    high_max = df['High'].rolling(k_period, min_periods=1).max()
    k = 100 * (df['Close'] - low_min) / (high_max - low_min).replace(0, 1e-10)
    d = k.rolling(d_period, min_periods=1).mean()
    return k, d

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

def compute_signals(df, df_daily, params):
    """Calcula señales BUY/SELL en el TF dado.
       Retorna long_cond, short_cond como Series booleanas."""
    if df.empty or len(df) < 100:
        empty = pd.Series([False] * len(df), index=df.index)
        return empty, empty

    ha = heikin_ashi(df)
    ha_o_ma = vwma(ha['open'], df['Volume'], params['ma_period'])
    ha_c_ma = vwma(ha['close'], df['Volume'], params['ma_period'])
    ha_o_sm = vwma(ha_o_ma, df['Volume'], params['ma_smooth'])
    ha_c_sm = vwma(ha_c_ma, df['Volume'], params['ma_smooth'])
    av2_bull = ha_c_sm >= ha_o_sm

    trend_st, _, _ = supertrend(df, params['st_period'], params['st_mult'])
    blue_bar, red_bar = qqe_mod(df['Close'])
    adx_v, plus_di, minus_di = adx_dmi(df, 14)
    strong = adx_v >= params['adx_threshold']

    d_trend, _ = daily_trend(df_daily, 20, 50)
    ok_long = (not params['use_daily']) or (d_trend >= 0)
    ok_short = (not params['use_daily']) or (d_trend <= 0)

    long_sig = av2_bull & (trend_st == 1) & blue_bar & strong & ok_long
    short_sig = (~av2_bull) & (trend_st == -1) & red_bar & strong & ok_short
    long_cond = long_sig & (~long_sig.shift(1).fillna(False))
    short_cond = short_sig & (~short_sig.shift(1).fillna(False))
    return long_cond, short_cond

# ============================================================
# SESIONES
# ============================================================
def get_session_now():
    now_utc = datetime.now(pytz.UTC)
    h = now_utc.hour
    weekday = now_utc.weekday()
    if weekday == 5:
        return []
    if weekday == 6 and h < 22:
        return []
    if weekday == 4 and h >= 22:
        return []
    sessions = []
    if h >= 22 or h < 7:
        sessions.append(("Sídney", "#FF6B35"))
    if h >= 0 and h < 9:
        sessions.append(("Tokio", "#FFD700"))
    if h >= 8 and h < 17:
        sessions.append(("Londres", "#4FC3F7"))
    if h >= 13 and h < 22:
        sessions.append(("Nueva York", "#9C27B0"))
    return sessions

def is_market_open(asset_type):
    """Forex/Metales cerrado fines de semana. Crypto siempre abierto."""
    if "Crypto" in asset_type:
        return True
    now_utc = datetime.now(pytz.UTC)
    weekday = now_utc.weekday()
    h = now_utc.hour
    if weekday == 5:
        return False
    if weekday == 6 and h < 22:
        return False
    if weekday == 4 and h >= 22:
        return False
    return True

def add_session_shading(fig, df_show):
    if df_show.empty:
        return
    start = df_show.index[0]
    end = df_show.index[-1]
    cur = start.replace(hour=0, minute=0, second=0, microsecond=0)
    sessions_def = [
        (22, 7,  "rgba(255,107,53,0.05)"),
        (0,  9,  "rgba(255,215,0,0.04)"),
        (8,  17, "rgba(79,195,247,0.06)"),
        (13, 22, "rgba(156,39,176,0.05)"),
    ]
    iter_count = 0
    while cur <= end + timedelta(days=1) and iter_count < 60:
        for sh, eh, col in sessions_def:
            if sh > eh:
                s1 = cur.replace(hour=sh)
                e1 = (cur + timedelta(days=1)).replace(hour=eh)
            else:
                s1 = cur.replace(hour=sh)
                e1 = cur.replace(hour=eh)
            if s1 > end or e1 < start:
                continue
            fig.add_vrect(x0=max(s1, start), x1=min(e1, end),
                          fillcolor=col, layer="below", line_width=0,
                          row=1, col=1)
        cur += timedelta(days=1)
        iter_count += 1

# ============================================================
# CARGAR DATOS — VIEW TF (gráfico) + SIGNAL TF (señales)
# ============================================================
with st.spinner(f"Cargando {sym_label}..."):
    # Datos del TF que se está viendo
    df = get_data(sym_code, tf_minutes, period)
    # Datos del TF maestro de señales (3M por defecto)
    df_signal = get_data(sym_code, sig_tf_min, period)
    # Diario (para filtro)
    df_daily = fetch_data(sym_code, "180d", "1d")

if df.empty or len(df) < 50:
    st.error(f"❌ No se cargaron datos para {sym_label}. Yahoo puede tener limitaciones para este símbolo o temporalidad. Prueba otra combinación.")
    st.stop()

if df_signal.empty or len(df_signal) < 50:
    st.warning(f"⚠️ No hay datos suficientes en {signal_tf} para calcular señales. Mostrando solo el gráfico sin flechas.")
    df_signal = df.copy()  # fallback

# ============================================================
# CALCULAR INDICADORES en TF visible
# ============================================================
ha = heikin_ashi(df)
ha_o_ma = vwma(ha['open'], df['Volume'], ma_period)
ha_c_ma = vwma(ha['close'], df['Volume'], ma_period)
ha_o_smooth = vwma(ha_o_ma, df['Volume'], ma_smooth)
ha_c_smooth = vwma(ha_c_ma, df['Volume'], ma_smooth)
av2_bull = ha_c_smooth >= ha_o_smooth

trend_st, st_upper, st_lower = supertrend(df, st_period, st_mult)
blue_bar, red_bar = qqe_mod(df['Close'])
adx_v, plus_di, minus_di = adx_dmi(df, 14)
strong = adx_v >= adx_threshold
ema20_v = df['Close'].ewm(span=20, adjust=False).mean()
ema100_v = df['Close'].ewm(span=100, adjust=False).mean()
bb_basis, bb_upper, bb_lower = bollinger(df['Close'], bb_period, bb_std)
stoch_k_v, stoch_d_v = stochastic(df, stoch_k, stoch_d)

d_trend, d_change = daily_trend(df_daily, 20, 50)

# ============================================================
# SEÑALES — calculadas SIEMPRE en signal_tf (3M default)
# ============================================================
sig_params = {
    'ma_period': ma_period, 'ma_smooth': ma_smooth,
    'st_period': st_period, 'st_mult': st_mult,
    'adx_threshold': adx_threshold, 'use_daily': use_daily,
}
long_cond_sig, short_cond_sig = compute_signals(df_signal, df_daily, sig_params)

# Mapear las señales del TF maestro al TF visible
# Por cada vela del TF visible, marcamos si dentro de su rango temporal
# ocurrió una señal en el TF maestro
def map_signals_to_view(view_idx, signals_idx, view_tf_min):
    """signals_idx: DatetimeIndex donde ocurrieron señales
       view_idx: DatetimeIndex del TF visible
       Retorna Series booleana sobre view_idx"""
    out = pd.Series(False, index=view_idx)
    if len(signals_idx) == 0:
        return out
    delta = pd.Timedelta(minutes=view_tf_min)
    for sig_t in signals_idx:
        # Encuentra la vela del TF visible que contiene este tiempo de señal
        candidates = view_idx[(view_idx <= sig_t) & (view_idx > sig_t - delta * 2)]
        if len(candidates) > 0:
            target = candidates[-1]
            out.loc[target] = True
        else:
            # Vela siguiente más cercana
            candidates = view_idx[view_idx >= sig_t]
            if len(candidates) > 0:
                out.loc[candidates[0]] = True
    return out

long_idx_sig = df_signal.index[long_cond_sig]
short_idx_sig = df_signal.index[short_cond_sig]
long_cond_view = map_signals_to_view(df.index, long_idx_sig, tf_minutes)
short_cond_view = map_signals_to_view(df.index, short_idx_sig, tf_minutes)

# ============================================================
# DETECCIÓN DE NUEVA SEÑAL (sonido)
# ============================================================
last_long_idx = long_idx_sig[-1] if len(long_idx_sig) > 0 else None
last_short_idx = short_idx_sig[-1] if len(short_idx_sig) > 0 else None

last_signal_time = None
last_signal_type = None
if last_long_idx is not None and last_short_idx is not None:
    if last_long_idx > last_short_idx:
        last_signal_time, last_signal_type = last_long_idx, "BUY"
    else:
        last_signal_time, last_signal_type = last_short_idx, "SELL"
elif last_long_idx is not None:
    last_signal_time, last_signal_type = last_long_idx, "BUY"
elif last_short_idx is not None:
    last_signal_time, last_signal_type = last_short_idx, "SELL"

new_signal = False
if last_signal_time is not None:
    age_min = (datetime.now(pytz.UTC) - last_signal_time).total_seconds() / 60
    new_signal = age_min < (sig_tf_min * 1.5)

if 'last_signal_played' not in st.session_state:
    st.session_state.last_signal_played = None

play_sound = False
if sound_on and new_signal and last_signal_time is not None:
    sig_id = f"{sym_code}_{last_signal_time.isoformat()}_{last_signal_type}"
    if st.session_state.last_signal_played != sig_id:
        play_sound = True
        st.session_state.last_signal_played = sig_id

# ============================================================
# STATUS BAR
# ============================================================
last_price = float(df['Close'].iloc[-1])
prev_price = float(df['Close'].iloc[-2])
price_change = ((last_price - prev_price) / prev_price) * 100

# Día H/L
candles_per_day = max(1, int(1440 / max(tf_minutes, 1)))
day_data = df.tail(candles_per_day)
day_high = float(day_data['High'].max())
day_low = float(day_data['Low'].min())

active_sessions = get_session_now()
market_open = is_market_open(category)

sessions_html = ""
for sname, scolor in [("Sídney", "#FF6B35"), ("Tokio", "#FFD700"),
                       ("Londres", "#4FC3F7"), ("Nueva York", "#9C27B0")]:
    is_active = any(s[0] == sname for s in active_sessions)
    if is_active:
        sessions_html += f'<span class="session-active" style="background: {scolor};">● {sname}</span> '
    else:
        sessions_html += f'<span class="session-closed">○ {sname}</span> '

market_status = '<span style="color:#26a69a;">● MERCADO ABIERTO</span>' if market_open else '<span style="color:#EF5350;">● MERCADO CERRADO</span>'
price_color = "#26a69a" if price_change >= 0 else "#ef5350"
arrow = "▲" if price_change >= 0 else "▼"
now_str = datetime.now(pytz.UTC).strftime('%H:%M:%S UTC')

# Decimales según instrumento
if "JPY" in sym_code or "INR" in sym_code or "MXN" in sym_code:
    fmt = "{:,.3f}"
elif "Crypto" in category and last_price < 1:
    fmt = "{:,.6f}"
elif "Crypto" in category:
    fmt = "{:,.2f}"
elif "USD=X" in sym_code or "=X" in sym_code:
    fmt = "{:,.5f}"
else:
    fmt = "{:,.2f}"

st.markdown(f"""
<div class="status-bar">
    <div>
        <strong style="font-size:0.95rem; color:#FFD700;">📊 {sym_label}</strong>
        <span style="color:white; margin-left:10px; font-size:0.95rem;">{fmt.format(last_price)}</span>
        <span style="color:{price_color}; margin-left:6px;">{arrow} {price_change:+.3f}%</span>
        <span style="margin-left:14px; color:#787b86;">H: <span style="color:#d1d4dc;">{fmt.format(day_high)}</span></span>
        <span style="margin-left:8px; color:#787b86;">L: <span style="color:#d1d4dc;">{fmt.format(day_low)}</span></span>
        <span style="margin-left:14px;">Vista: <strong>{tf_label}</strong> · Señales: <strong style="color:#FFD700;">{signal_tf}</strong></span>
    </div>
    <div style="text-align:right;">
        {sessions_html}
        <span style="margin-left:10px;">{market_status}</span>
        <span style="margin-left:10px; color:#787b86;">{now_str}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PANEL DE CONFIRMACIONES
# ============================================================
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

stoch_now = float(stoch_k_v.iloc[-1]) if not pd.isna(stoch_k_v.iloc[-1]) else 50
stoch_status = "🔴 SOBRECOMPRA" if stoch_now > 80 else "🟢 SOBREVENTA" if stoch_now < 20 else "⚪ NEUTRAL"
adx_now = float(adx_v.iloc[-1]) if not pd.isna(adx_v.iloc[-1]) else 0

c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1, 1, 1, 1, 1.4])
d_label = "🟢 ALCISTA" if d_trend == 1 else "🔴 BAJISTA" if d_trend == -1 else "🟡 LATERAL"
c1.metric("📅 Daily", d_label, f"{d_change:+.2f}%")
c2.metric("⚡ ADX", f"{adx_now:.1f}", "FUERTE" if adx_now >= adx_threshold else "DÉBIL")
c3.metric("📈 A-V2", "ALCISTA" if av2_bull.iloc[-1] else "BAJISTA")
c4.metric("📊 ST", "ALCISTA" if trend_st.iloc[-1] == 1 else "BAJISTA")
c5.metric("🎯 QQE", "COMPRA" if blue_bar.iloc[-1] else "VENTA" if red_bar.iloc[-1] else "—")
c6.metric("📉 Stoch", f"{stoch_now:.0f}", stoch_status)
c7.metric("💪 FUERZA", f"{score_emoji} {final_score}%", direction)

# ============================================================
# GRÁFICO PRINCIPAL
# ============================================================
df_show = df.tail(candles_to_show).copy()
ha_o_s = ha_o_smooth.tail(candles_to_show)
ha_c_s = ha_c_smooth.tail(candles_to_show)
trend_st_s = trend_st.tail(candles_to_show)
st_upper_s = st_upper.tail(candles_to_show)
st_lower_s = st_lower.tail(candles_to_show)
ema20_s = ema20_v.tail(candles_to_show)
ema100_s = ema100_v.tail(candles_to_show)
bb_basis_s = bb_basis.tail(candles_to_show)
bb_upper_s = bb_upper.tail(candles_to_show)
bb_lower_s = bb_lower.tail(candles_to_show)
adx_s = adx_v.tail(candles_to_show)
plus_di_s = plus_di.tail(candles_to_show)
minus_di_s = minus_di.tail(candles_to_show)
stoch_k_s = stoch_k_v.tail(candles_to_show)
stoch_d_s = stoch_d_v.tail(candles_to_show)
long_cond_s = long_cond_view.tail(candles_to_show)
short_cond_s = short_cond_view.tail(candles_to_show)

# Heikin Ashi del TF visible (para chart_type)
ha_view = heikin_ashi(df_show)

# Configuración subplots según volume
n_rows = 4 if show_volume else 3
heights = [0.58, 0.14, 0.14, 0.14] if show_volume else [0.66, 0.17, 0.17]

fig = make_subplots(
    rows=n_rows, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.015,
    row_heights=heights,
)

# Sesiones background
if show_sessions:
    add_session_shading(fig, df_show)

# ---------- ROW 1: PRECIO según chart_type ----------
inc_color = '#26A69A'
dec_color = '#EF5350'

if chart_type == "🕯️ Velas":
    fig.add_trace(go.Candlestick(
        x=df_show.index,
        open=df_show['Open'], high=df_show['High'],
        low=df_show['Low'], close=df_show['Close'],
        name='Precio',
        increasing_line_color=inc_color, decreasing_line_color=dec_color,
        increasing_fillcolor=inc_color, decreasing_fillcolor=dec_color,
        line=dict(width=1), showlegend=False,
    ), row=1, col=1)

elif chart_type == "🟩 Heikin Ashi":
    fig.add_trace(go.Candlestick(
        x=df_show.index,
        open=ha_view['open'], high=ha_view['high'],
        low=ha_view['low'], close=ha_view['close'],
        name='Heikin Ashi',
        increasing_line_color=inc_color, decreasing_line_color=dec_color,
        increasing_fillcolor=inc_color, decreasing_fillcolor=dec_color,
        line=dict(width=1), showlegend=False,
    ), row=1, col=1)

elif chart_type == "📉 Línea":
    fig.add_trace(go.Scatter(
        x=df_show.index, y=df_show['Close'],
        mode='lines', line=dict(color='#FFD700', width=2),
        name='Precio', showlegend=False,
    ), row=1, col=1)

elif chart_type == "🌊 Área":
    fig.add_trace(go.Scatter(
        x=df_show.index, y=df_show['Close'],
        mode='lines', line=dict(color='#FFD700', width=2),
        fill='tozeroy', fillcolor='rgba(255,215,0,0.15)',
        name='Precio', showlegend=False,
    ), row=1, col=1)

elif chart_type == "📊 OHLC Bars":
    fig.add_trace(go.Ohlc(
        x=df_show.index,
        open=df_show['Open'], high=df_show['High'],
        low=df_show['Low'], close=df_show['Close'],
        name='OHLC',
        increasing_line_color=inc_color, decreasing_line_color=dec_color,
        showlegend=False,
    ), row=1, col=1)

elif chart_type == "⬜ Velas huecas":
    fig.add_trace(go.Candlestick(
        x=df_show.index,
        open=df_show['Open'], high=df_show['High'],
        low=df_show['Low'], close=df_show['Close'],
        name='Hollow',
        increasing_line_color=inc_color, decreasing_line_color=dec_color,
        increasing_fillcolor='rgba(0,0,0,0)',  # hueco
        decreasing_fillcolor=dec_color,
        line=dict(width=1.5), showlegend=False,
    ), row=1, col=1)

# Bollinger
if show_bb:
    fig.add_trace(go.Scatter(x=bb_upper_s.index, y=bb_upper_s, mode='lines',
                              line=dict(color='#FFA726', width=2),
                              name='BB Upper', opacity=0.85), row=1, col=1)
    fig.add_trace(go.Scatter(x=bb_basis_s.index, y=bb_basis_s, mode='lines',
                              line=dict(color='#FFA726', width=1.5, dash='dot'),
                              name='BB Basis', opacity=0.7), row=1, col=1)
    fig.add_trace(go.Scatter(x=bb_lower_s.index, y=bb_lower_s, mode='lines',
                              line=dict(color='#FFA726', width=2),
                              fill='tonexty', fillcolor='rgba(255,167,38,0.06)',
                              name='BB Lower', opacity=0.85), row=1, col=1)

if show_ema20:
    fig.add_trace(go.Scatter(x=ema20_s.index, y=ema20_s, mode='lines',
                              line=dict(color='#00E5FF', width=2.5),
                              name='EMA 20'), row=1, col=1)
if show_ema100:
    fig.add_trace(go.Scatter(x=ema100_s.index, y=ema100_s, mode='lines',
                              line=dict(color='#E040FB', width=2.5),
                              name='EMA 100'), row=1, col=1)

if show_cloud:
    fig.add_trace(go.Scatter(x=ha_o_s.index, y=ha_o_s, mode='lines',
                              line=dict(color='rgba(0,0,0,0)', width=0),
                              showlegend=False, hoverinfo='skip'), row=1, col=1)
    fig.add_trace(go.Scatter(x=ha_c_s.index, y=ha_c_s, mode='lines',
                              line=dict(color='rgba(0,0,0,0)', width=0),
                              fill='tonexty', fillcolor='rgba(38,166,154,0.10)',
                              name='A-V2', hoverinfo='skip', showlegend=False), row=1, col=1)

if show_st_lines:
    st_up_plot = st_upper_s.where(trend_st_s == 1)
    st_dn_plot = st_lower_s.where(trend_st_s == -1)
    fig.add_trace(go.Scatter(x=st_up_plot.index, y=st_up_plot, mode='lines',
                              line=dict(color='#00C853', width=2.5),
                              name='ST Up'), row=1, col=1)
    fig.add_trace(go.Scatter(x=st_dn_plot.index, y=st_dn_plot, mode='lines',
                              line=dict(color='#FF1744', width=2.5),
                              name='ST Down'), row=1, col=1)

# Señales BUY/SELL — del TF maestro proyectadas al TF visible
if show_signals:
    buy_pts = df_show[long_cond_s]
    sell_pts = df_show[short_cond_s]
    if not buy_pts.empty:
        fig.add_trace(go.Scatter(
            x=buy_pts.index, y=buy_pts['Low'] * 0.9985,
            mode='markers+text', text=[f'BUY ({signal_tf})'] * len(buy_pts),
            textposition='bottom center',
            textfont=dict(color='#00E676', size=9, family='Arial Black'),
            marker=dict(symbol='triangle-up', size=14, color='#00E676',
                        line=dict(color='white', width=1.5)),
            name='BUY', showlegend=False), row=1, col=1)
    if not sell_pts.empty:
        fig.add_trace(go.Scatter(
            x=sell_pts.index, y=sell_pts['High'] * 1.0015,
            mode='markers+text', text=[f'SELL ({signal_tf})'] * len(sell_pts),
            textposition='top center',
            textfont=dict(color='#FF1744', size=9, family='Arial Black'),
            marker=dict(symbol='triangle-down', size=14, color='#FF1744',
                        line=dict(color='white', width=1.5)),
            name='SELL', showlegend=False), row=1, col=1)

# ---------- VOLUMEN (opcional) ----------
if show_volume:
    vol_colors = ['#26A69A' if c >= o else '#EF5350'
                  for c, o in zip(df_show['Close'], df_show['Open'])]
    fig.add_trace(go.Bar(x=df_show.index, y=df_show['Volume'],
                          marker_color=vol_colors, name='Volume',
                          showlegend=False, opacity=0.6), row=2, col=1)
    fig.add_annotation(text="Volume", xref="x2 domain", yref="y2 domain",
                        x=0.01, y=0.95, showarrow=False,
                        font=dict(size=10, color="#787b86"), row=2, col=1)
    adx_row, stoch_row = 3, 4
else:
    adx_row, stoch_row = 2, 3

# ---------- ADX ----------
fig.add_trace(go.Scatter(x=adx_s.index, y=adx_s, mode='lines',
                          line=dict(color='#FFD700', width=2),
                          name='ADX', showlegend=False), row=adx_row, col=1)
fig.add_trace(go.Scatter(x=plus_di_s.index, y=plus_di_s, mode='lines',
                          line=dict(color='#26A69A', width=1.3),
                          name='DI+', showlegend=False), row=adx_row, col=1)
fig.add_trace(go.Scatter(x=minus_di_s.index, y=minus_di_s, mode='lines',
                          line=dict(color='#EF5350', width=1.3),
                          name='DI-', showlegend=False), row=adx_row, col=1)
fig.add_hline(y=adx_threshold, line=dict(color='#787b86', width=1, dash='dash'),
              row=adx_row, col=1)
fig.add_annotation(text="ADX", xref=f"x{adx_row} domain", yref=f"y{adx_row} domain",
                    x=0.01, y=0.95, showarrow=False,
                    font=dict(size=10, color="#FFD700"), row=adx_row, col=1)

# ---------- STOCHASTIC ----------
fig.add_trace(go.Scatter(x=stoch_k_s.index, y=stoch_k_s, mode='lines',
                          line=dict(color='#42A5F5', width=2),
                          name='%K', showlegend=False), row=stoch_row, col=1)
fig.add_trace(go.Scatter(x=stoch_d_s.index, y=stoch_d_s, mode='lines',
                          line=dict(color='#FF7043', width=2),
                          name='%D', showlegend=False), row=stoch_row, col=1)
fig.add_hline(y=80, line=dict(color='#EF5350', width=1, dash='dash'), row=stoch_row, col=1)
fig.add_hline(y=20, line=dict(color='#26A69A', width=1, dash='dash'), row=stoch_row, col=1)
fig.add_hrect(y0=80, y1=100, fillcolor="rgba(239,83,80,0.10)", line_width=0, row=stoch_row, col=1)
fig.add_hrect(y0=0, y1=20, fillcolor="rgba(38,166,154,0.10)", line_width=0, row=stoch_row, col=1)
fig.add_annotation(text="Stoch %K %D",
                    xref=f"x{stoch_row} domain", yref=f"y{stoch_row} domain",
                    x=0.01, y=0.95, showarrow=False,
                    font=dict(size=10, color="#42A5F5"), row=stoch_row, col=1)

# ============================================================
# LAYOUT
# ============================================================
chart_height = 760 if show_volume else 720
fig.update_layout(
    template='plotly_dark',
    height=chart_height,
    margin=dict(l=8, r=8, t=8, b=8),
    showlegend=True,
    legend=dict(
        orientation='h', yanchor='top', y=1.0, xanchor='left', x=0,
        bgcolor='rgba(19,23,34,0.7)', bordercolor='#2a2e39', borderwidth=1,
        font=dict(size=10, color='#d1d4dc'),
    ),
    xaxis_rangeslider_visible=False,
    dragmode='pan',
    newshape=dict(line=dict(color='#FFD700', width=2)),
    hovermode='x unified',
    paper_bgcolor='#131722',
    plot_bgcolor='#131722',
    font=dict(family='Trebuchet MS, sans-serif', size=10, color='#d1d4dc'),
)

for r in range(1, n_rows + 1):
    fig.update_xaxes(
        gridcolor='#1e222d', gridwidth=1,
        zeroline=False, showspikes=True,
        spikecolor='#787b86', spikethickness=1, spikedash='solid',
        spikemode='across', row=r, col=1,
    )
    fig.update_yaxes(
        gridcolor='#1e222d', gridwidth=1,
        zeroline=False, showspikes=True,
        spikecolor='#787b86', spikethickness=1, spikedash='solid',
        side='right', row=r, col=1,
    )

# Range breaks fines de semana (no para crypto)
if tf_minutes < 1440 and "Crypto" not in category:
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

fig.update_yaxes(range=[0, 100], row=stoch_row, col=1)

config = {
    'scrollZoom': True,
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': [
        'drawline', 'drawopenpath', 'drawclosedpath',
        'drawcircle', 'drawrect', 'eraseshape',
    ],
    'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': f'TAV3_{sym_code.replace("=","").replace("^","")}_{tf_label}',
        'height': 900, 'width': 1800, 'scale': 2,
    },
}
st.plotly_chart(fig, use_container_width=True, config=config)

# ============================================================
# SONIDO + BANNER
# ============================================================
if play_sound and last_signal_time is not None and last_signal_type is not None:
    sig_price = float(df_signal.loc[last_signal_time, 'Close'])
    banner_class = "signal-banner" if last_signal_type == "BUY" else "signal-banner-sell"
    components.html(f"""
    <script>
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const playBell = (freq, duration, delay) => {{
                setTimeout(() => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.value = freq;
                    gain.gain.setValueAtTime(0.3, ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + duration);
                }}, delay);
            }};
            playBell(880, 0.4, 0);
            playBell(1320, 0.4, 100);
            playBell(880, 0.6, 250);
        }} catch(e) {{ console.log('Audio:', e); }}
    </script>
    <div class="{banner_class}">
        🔔 NUEVA SEÑAL ({signal_tf}) — {last_signal_type} {sym_label} @ {fmt.format(sig_price)} · {last_signal_time.strftime('%H:%M UTC')}
    </div>
    <style>
        .signal-banner {{
            background: linear-gradient(90deg, #00E676 0%, #00C853 100%);
            color: #000; padding: 8px 16px; border-radius: 4px;
            font-weight: bold; text-align: center; font-size: 0.9rem; margin: 4px 0;
        }}
        .signal-banner-sell {{
            background: linear-gradient(90deg, #FF1744 0%, #D50000 100%);
            color: white; padding: 8px 16px; border-radius: 4px;
            font-weight: bold; text-align: center; font-size: 0.9rem; margin: 4px 0;
        }}
    </style>
    """, height=60)

# ============================================================
# RECOMENDACIÓN
# ============================================================
if final_score >= 80:
    st.success(f"✅ **OPERAR {direction}** — Triple confirmación + tendencia diaria a favor + ADX fuerte ({final_score}%) · Señales del TF {signal_tf}")
elif final_score >= 60:
    st.warning(f"⚠️ **ESPERAR mejor entrada** — Confirmación parcial ({final_score}%)")
else:
    st.error(f"❌ **NO OPERAR** — Sin confirmación clara ({final_score}%)")

# ============================================================
# TABLA DE SEÑALES
# ============================================================
with st.expander(f"📋 Últimas señales ({signal_tf})", expanded=False):
    signals = []
    for idx in df_signal.index[long_cond_sig]:
        signals.append({'Hora UTC': idx, 'Tipo': '🟢 BUY',
                        'Precio': df_signal.loc[idx, 'Close']})
    for idx in df_signal.index[short_cond_sig]:
        signals.append({'Hora UTC': idx, 'Tipo': '🔴 SELL',
                        'Precio': df_signal.loc[idx, 'Close']})
    if signals:
        df_sig_tbl = pd.DataFrame(signals).sort_values('Hora UTC', ascending=False).head(20)
        df_sig_tbl['Precio'] = df_sig_tbl['Precio'].apply(lambda x: fmt.format(x))
        st.dataframe(df_sig_tbl, use_container_width=True, hide_index=True)
    else:
        st.info("Sin señales aún en este TF.")

st.caption(f"📡 Yahoo Finance · Auto-refresh 30s · Delay ~15min · Dibujo en barra superior · "
           f"Señales: <b>{signal_tf}</b> proyectadas al gráfico de <b>{tf_label}</b>",
           unsafe_allow_html=True)
