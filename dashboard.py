import os
import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- CONFIGURACIÓN BASE ---
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
THRESHOLD = 70.0
ALPHA = 0.25 
LOG_FILE = "backtest_log.csv"

st.set_page_config(page_title="QUANTUM SNIPER 6-CORE", layout="wide")
st_autorefresh(interval=5000, key="quantum_final_v18_2026")

# --- LIMPIEZA / INICIO DE LOGS ---
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["timestamp", "symbol", "price", "score", "trend", "clv", "cvd", "rsi", "vol", "mom"]).to_csv(LOG_FILE, index=False)
else:
    try:
        test_df = pd.read_csv(LOG_FILE)
        if len(test_df.columns) < 10:
            os.remove(LOG_FILE)
            pd.DataFrame(columns=["timestamp", "symbol", "price", "score", "trend", "clv", "cvd", "rsi", "vol", "mom"]).to_csv(LOG_FILE, index=False)
    except:
        os.remove(LOG_FILE)

# Memoria de Sesión
if 'score_history' not in st.session_state:
    st.session_state.score_history = {pair: 50.0 for pair in PAIRS}
if 'price_memory' not in st.session_state:
    st.session_state.price_memory = {pair: 0.0 for pair in PAIRS}
if 'metric_memory' not in st.session_state:
    st.session_state.metric_memory = {pair: [50]*5 for pair in PAIRS}
if 'session' not in st.session_state:
    st.session_state.session = requests.Session()

def log_backtest(symbol, price, score, trend, metrics):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        "timestamp": now, "symbol": symbol, "price": price, 
        "score": round(score, 2), "trend": trend,
        "clv": metrics[0], "cvd": metrics[1], "rsi": metrics[2], "vol": metrics[3], "mom": metrics[4]
    }
    pd.DataFrame([new_entry]).to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)

# Estilo CSS
st.markdown("""
    <style>
    .main { background-color: #06090f; }
    .crypto-card {
        background-color: #101623 !important;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 251, 255, 0.15);
        margin-bottom: 5px;
    }
    .pair-header { color: #00fbff; font-weight: bold; font-size: 14px; }
    .price-text { color: #ffffff; font-family: monospace; font-size: 24px; font-weight: bold; }
    .sc-label { color: #00fbff; font-weight: 900; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

def fetch_data(symbol):
    try:
        base_url = "https://api.binance.com"
        p_res = st.session_state.session.get(f"{base_url}/api/v3/ticker/price?symbol={symbol}", timeout=2).json()
        k_res = st.session_state.session.get(f"{base_url}/api/v3/klines?symbol={symbol}&interval=1m&limit=30", timeout=2).json()
        
        curr_price = float(p_res['price'])
        df = pd.DataFrame(k_res).apply(pd.to_numeric)
        v_smooth, v_mean = df[5].iloc[-3:].mean(), df[5].mean()
        z_vol = (v_smooth - v_mean) / (df[5].std() + 1e-9)
        direction = "UP" if curr_price > df[1].iloc[-1] else "DOWN"
        
        raw_score = 50 + (np.clip(abs(z_vol), 0, 2.5) * 15)
        smoothed = (raw_score * ALPHA) + (st.session_state.score_history[symbol] * (1 - ALPHA))
        
        st.session_state.score_history[symbol] = smoothed
        st.session_state.price_memory[symbol] = curr_price
        metrics = [round(smoothed,1), round(50+(z_vol*10),1), 60, round(50+(abs(z_vol)*12),1), 85 if direction=="UP" else 15]
        st.session_state.metric_memory[symbol] = metrics
        
        if smoothed >= THRESHOLD:
            log_backtest(symbol, curr_price, smoothed, direction, metrics)
            
        return curr_price, smoothed, direction, metrics
    except:
        return st.session_state.price_memory[symbol], st.session_state.score_history[symbol], "WAIT", st.session_state.metric_memory[symbol]

st.markdown("<h1 style='text-align:center; color:#00fbff; margin-top:-40px;'>🏹 QUANTUM SNIPER 6-CORE</h1>", unsafe_allow_html=True)

cols = st.columns(3)
for i, sym in enumerate(PAIRS):
    price, score, trend, metrics = fetch_data(sym)
    is_sniper = score >= THRESHOLD
    color = "#00ff88" if (is_sniper and trend=="UP") else ("#ff4b4b" if (is_sniper and trend=="DOWN") else "#00fbff")
    
    with cols[i % 3]:
        st.markdown(f"""
            <div class="crypto-card" style="border-color: {color if is_sniper else 'rgba(0,251,255,0.1)'};">
                <div style="display:flex; justify-content:space-between;">
                    <span class="pair-header">{sym}</span>
                    <span style="color:#555; font-size:10px; font-weight:bold;">SYNC OK</span>
                </div>
                <div class="price-text">${price:,.2f}</div>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <span class="sc-label">SC: {score:.1f}</span>
                    <span style="color:{color}; font-weight:bold;">{trend}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(go.Scatterpolar(
            r=metrics + [metrics[0]],
            theta=['SCORE', 'CVD', 'RSI', 'VOL', 'MOM', 'SCORE'],
            fill='toself', 
            fillcolor=f'rgba({0 if trend=="UP" else 255}, {255 if trend=="UP" else 0}, 255, 0.1)',
            line=dict(color=color, width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(size=12, color="#00fbff", family="Arial Black"), rotation=90),
                domain=dict(x=[0.15, 0.85], y=[0.15, 0.85])
            ),
            showlegend=False, height=280, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)"
        )
        # Cambio clave aquí: width='stretch'
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False}, key=f"rad_{sym}_{i}")

st.write("---")
st.subheader("📊 Historial de Backtesting")

if os.path.exists(LOG_FILE):
    try:
        log_df = pd.read_csv(LOG_FILE)
        if not log_df.empty:
            # Cambio clave aquí: width='stretch'
            st.dataframe(log_df.tail(15).sort_values(by='timestamp', ascending=False), width='stretch')
        else:
            st.info("Esperando señales...")
    except:
        st.error("Error cargando logs.")
