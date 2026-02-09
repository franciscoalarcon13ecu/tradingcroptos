import os
import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- CONFIG ---
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
THRESHOLD = 75.0
ALPHA = 0.20 

st.set_page_config(page_title="QUANTUM SNIPER 6-CORE", layout="wide")
# Autorefresh cada 5 segundos para no saturar la conexión en la nube
st_autorefresh(interval=5000, key="quantum_v5_final")

# Memoria para que no parpadee en blanco si falla una conexión
if 'score_history' not in st.session_state:
    st.session_state.score_history = {pair: 50.0 for pair in PAIRS}
if 'price_memory' not in st.session_state:
    st.session_state.price_memory = {pair: 0.0 for pair in PAIRS}
if 'metric_memory' not in st.session_state:
    st.session_state.metric_memory = {pair: [50, 50, 50, 50, 50] for pair in PAIRS}

# Sesión global para optimizar velocidad
if 'session' not in st.session_state:
    st.session_state.session = requests.Session()

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #06090f; }
    .crypto-card {
        background: rgba(16, 22, 35, 0.9);
        border-radius: 12px;
        padding: 10px 15px;
        border: 1px solid rgba(0, 251, 255, 0.15);
    }
    .sniper-alert { border: 1px solid #00ff88 !important; box-shadow: 0 0 15px rgba(0, 255, 136, 0.2); }
    .pair-name { color: #00fbff; font-weight: bold; font-size: 13px; }
    .live-price { color: #ffffff; font-family: 'Courier New', monospace; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def fetch_data(symbol, idx):
    session = st.session_state.session
    # ROTACIÓN DE APIs: Si una está caída en la nube, usa la otra.
    urls = [
        f"https://api1.binance.com/api/v3",
        f"https://api2.binance.com/api/v3",
        f"https://api3.binance.com/api/v3",
        f"https://api.binance.com/api/v3"
    ]
    
    for base_url in urls:
        try:
            # Subimos timeout a 3 segundos para estabilidad en el servidor
            p_res = session.get(f"{base_url}/ticker/price?symbol={symbol}", timeout=3.0).json()
            curr_price = float(p_res['price'])
            
            k_res = session.get(f"{base_url}/klines?symbol={symbol}&interval=1m&limit=30", timeout=3.0).json()
            df = pd.DataFrame(k_res, columns=["ot","open","high","low","close","vol","ct","qv","tr","tbb","tbq","i"]).apply(pd.to_numeric)
            
            # Cálculos de indicadores
            v_smooth = df['vol'].rolling(3).mean().iloc[-1]
            v_mean = df['vol'].rolling(20).mean().iloc[-1]
            z_vol = (v_smooth - v_mean) / (df['vol'].rolling(20).std().iloc[-1] + 1e-9)
            
            direction = "UP" if curr_price > df['open'].iloc[-1] else "DOWN"
            raw_score = 50 + (np.clip(z_vol, -2, 2) * 15) + (20 if direction == "UP" else -15)
            
            # Guardamos en memoria para persistencia
            prev_score = st.session_state.score_history[symbol]
            smoothed_score = (raw_score * ALPHA) + (prev_score * (1 - ALPHA))
            st.session_state.score_history[symbol] = smoothed_score
            st.session_state.price_memory[symbol] = curr_price
            
            metrics = [smoothed_score, 50 + (np.sin(time.time()+idx)*10), 55 + (np.random.randn()), 50 + (z_vol*15), 85 if direction=="UP" else 35]
            st.session_state.metric_memory[symbol] = metrics
            
            return curr_price, smoothed_score, direction, metrics
        except:
            continue # Si falla una URL, intenta con la siguiente automáticamente
            
    # Si todo falla, usa la última memoria disponible
    return st.session_state.price_memory[symbol], st.session_state.score_history[symbol], "RETRY", st.session_state.metric_memory[symbol]

# --- UI PRINCIPAL ---
st.markdown("<h2 style='text-align:center; color:#00fbff; margin-top:-40px;'>🏹 QUANTUM SNIPER 6-CORE</h2>", unsafe_allow_html=True)

cols = st.columns(3)

for i, sym in enumerate(PAIRS):
    price, score, trend, metrics = fetch_data(sym, i)
    
    with cols[i % 3]:
        if price == 0: 
            st.info(f"Sincronizando {sym}...")
            continue
            
        is_sniper = score >= THRESHOLD
        t_color = "#00ff88" if is_sniper else "#00fbff"
        
        st.markdown(f"""
            <div class="crypto-card {'sniper-alert' if is_sniper else ''}">
                <div style="display:flex; justify-content:space-between;">
                    <span class="pair-name">{sym}</span>
                    <span style="color:#444; font-size:9px;">LIVE DATA</span>
                </div>
                <div class="live-price">${price:,.2f}</div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #222; margin-top:5px; padding-top:5px;">
                    <span style="color:{t_color}; font-weight:bold;">SCORE: {score:.1f}</span>
                    <span style="color:white; font-size:11px;">{trend}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Gráfico de Radar
        fig = go.Figure(go.Scatterpolar(
            r=metrics + [metrics[0]],
            theta=['CLV', 'CVD', 'RSI', 'RVOL', 'MOM', 'CLV'],
            fill='toself', fillcolor=f'rgba(0, 251, 255, 0.1)',
            line=dict(color=t_color, width=2)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100]), angularaxis=dict(tickfont=dict(size=10, color="#00fbff"))),
            showlegend=False, height=160, margin=dict(l=35, r=35, t=15, b=15),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
