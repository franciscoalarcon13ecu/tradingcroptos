import os, requests, numpy as np, pandas as pd, streamlit as st, plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- CONFIGURACIÓN ---
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
THRESHOLD = 70.0
ALPHA = 0.25 
LOG_FILE = "backtest_log.csv"

st.set_page_config(page_title="QUANTUM SNIPER 6-CORE", layout="wide")
st_autorefresh(interval=5000, key="resurrection_feb10")

# --- MEMORIA ---
if 'score_history' not in st.session_state:
    st.session_state.score_history = {pair: 50.0 for pair in PAIRS}
if 'price_memory' not in st.session_state:
    st.session_state.price_memory = {pair: 0.0 for pair in PAIRS}

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #06090f; }
    .crypto-card {
        background-color: #101623 !important;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #00fbff26;
        margin-bottom: 5px;
    }
    .pair-header { color: #00fbff; font-weight: bold; font-size: 14px; }
    .price-text { color: #ffffff; font-family: monospace; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def fetch_data(symbol):
    try:
        # Usamos API1 (generalmente más estable post-bloqueo)
        url_p = f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}"
        url_k = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=20" # Bajamos a 20 para ser más ligeros
        
        p_res = requests.get(url_p, timeout=2).json()
        curr_price = float(p_res['price'])
        
        k_res = requests.get(url_k, timeout=2).json()
        df = pd.DataFrame(k_res).apply(pd.to_numeric)
        
        v_smooth, v_mean = df[5].iloc[-3:].mean(), df[5].mean()
        z_vol = (v_smooth - v_mean) / (df[5].std() + 1e-9)
        direction = "UP" if curr_price > df[1].iloc[-1] else "DOWN"
        
        raw_score = 50 + (np.clip(abs(z_vol), 0, 2.5) * 15)
        smoothed = (raw_score * ALPHA) + (st.session_state.score_history[symbol] * (1 - ALPHA))
        st.session_state.score_history[symbol] = smoothed
        st.session_state.price_memory[symbol] = curr_price
        
        metrics = [round(smoothed,1), round(50+(z_vol*10),1), 60, round(50+(abs(z_vol)*12),1), 85 if direction=="UP" else 15]
        return curr_price, smoothed, direction, metrics
    except:
        return st.session_state.price_memory[symbol], st.session_state.score_history[symbol], "WAIT", [50]*5

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER PRO</h1>", unsafe_allow_html=True)

cols = st.columns(3)
for i, sym in enumerate(PAIRS):
    price, score, trend, metrics = fetch_data(sym)
    color = "#00ff88" if (score >= THRESHOLD and trend=="UP") else ("#ff4b4b" if (score >= THRESHOLD and trend=="DOWN") else "#00fbff")
    
    with cols[i % 3]:
        st.markdown(f"""
            <div class="crypto-card" style="border-left: 5px solid {color};">
                <span class="pair-header">{sym}</span>
                <div class="price-text">${price:,.2f}</div>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <span style="color:{color}; font-weight:bold; font-size:18px;">SC: {score:.1f}</span>
                    <span style="color:{color}; font-weight:bold;">{trend}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(go.Scatterpolar(r=metrics + [metrics[0]], theta=['SCORE','CVD','RSI','VOL','MOM','SCORE'], fill='toself', line=dict(color=color, width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), height=220, margin=dict(l=40,r=40,t=20,b=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"rad_{sym}")
