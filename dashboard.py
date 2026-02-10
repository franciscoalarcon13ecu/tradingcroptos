import os
import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- CONFIGURACIÓN ---
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
LOG_FILE = "backtest_log.csv"
st.set_page_config(page_title="QUANTUM SNIPER LIVE", layout="wide")
st_autorefresh(interval=5000, key="quantum_refresh_global")

# Inicializar archivo de log si no existe (Evita error de carga)
if not os.path.exists(LOG_FILE):
    df_init = pd.DataFrame(columns=["timestamp", "symbol", "price", "score", "trend", "clv", "cvd", "rsi", "vol", "mom"])
    df_init.to_csv(LOG_FILE, index=False)

# Inicializar memoria
if 'score_history' not in st.session_state:
    st.session_state.score_history = {pair: 50.0 for pair in PAIRS}

# --- FUNCIÓN DE DATOS CON "BYPASS" ---
def fetch_data(symbol):
    try:
        # Intentamos con la API principal de Binance
        # Usamos un timeout corto para que no se congele la app
        url_price = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        url_klines = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=30"
        
        p_res = requests.get(url_price, timeout=2).json()
        k_res = requests.get(url_klines, timeout=2).json()
        
        curr_price = float(p_res['price'])
        df = pd.DataFrame(k_res).apply(pd.to_numeric)
        
        # Lógica de cálculo (Z-Score de volumen)
        v_smooth = df[5].iloc[-3:].mean()
        v_mean = df[5].mean()
        z_vol = (v_smooth - v_mean) / (df[5].std() + 1e-9)
        
        direction = "UP" if curr_price > df[1].iloc[-1] else "DOWN"
        raw_score = 50 + (np.clip(abs(z_vol), 0, 2.5) * 15)
        
        # Suavizado para que no salte locamente
        smoothed = (raw_score * 0.25) + (st.session_state.score_history[symbol] * 0.75)
        st.session_state.score_history[symbol] = smoothed
        
        # Métricas para el Radar
        metrics = [round(smoothed,1), round(50+(z_vol*10),1), 60, round(50+(abs(z_vol)*12),1), 85 if direction=="UP" else 15]
        return curr_price, smoothed, direction, metrics
    except Exception as e:
        # Si falla (Binance bloqueó la IP de Streamlit), devolvemos valores neutros pero avisamos
        return 0.0, 50.0, "API WAIT", [50, 50, 50, 50, 50]

# --- RENDERIZADO ---
st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER LIVE</h1>", unsafe_allow_html=True)

# CSS
st.markdown("""<style>
    .crypto-card { background-color: #101623; border-radius: 12px; padding: 15px; border: 1px solid #1d2636; }
    .price-text { color: white; font-size: 24px; font-weight: bold; }
    </style>""", unsafe_allow_html=True)

cols = st.columns(3)
for i, sym in enumerate(PAIRS):
    price, score, trend, metrics = fetch_data(sym)
    color = "#00ff88" if trend == "UP" else "#ff4b4b"
    
    with cols[i % 3]:
        st.markdown(f"""<div class="crypto-card">
            <span style="color:#00fbff;">{sym}</span><br>
            <span class="price-text">${price:,.2f}</span><br>
            <span style="color:{color};">Trend: {trend} | SC: {score:.1f}</span>
        </div>""", unsafe_allow_html=True)
        
        # Radar
        fig = go.Figure(go.Scatterpolar(
            r=metrics + [metrics[0]],
            theta=['SC', 'CVD', 'RSI', 'VOL', 'MOM', 'SC'],
            fill='toself', line=dict(color=color)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100]), 
            angularaxis=dict(tickfont=dict(size=10, color="white"), rotation=90)),
            showlegend=False, height=250, margin=dict(l=40, r=40, t=30, b=30), paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True, key=f"cloud_rad_{sym}")

# Backtesting Table
st.write("---")
st.subheader("📊 Historial Reciente")
log_df = pd.read_csv(LOG_FILE)
st.dataframe(log_df.tail(10), use_container_width=True)
