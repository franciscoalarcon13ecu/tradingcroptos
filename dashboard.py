import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- CONFIG ---
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
THRESHOLD = 75.0

st.set_page_config(page_title="QUANTUM SNIPER 6-CORE", layout="wide")
# Refresco cada 5 segundos para estabilidad
st_autorefresh(interval=5000, key="quantum_final_refresh")

# Memoria para el Score
if 'score_mem' not in st.session_state:
    st.session_state.score_mem = {pair: 50.0 for pair in PAIRS}

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #06090f; }
    .crypto-card {
        background: rgba(16, 22, 35, 0.9);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 251, 255, 0.2);
        margin-bottom: 10px;
        text-align: center;
    }
    .pair-name { color: #00fbff; font-weight: bold; font-size: 18px; }
    .live-price { color: #ffffff; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_data(symbol):
    # Intentamos con api1 que es más estable para servidores
    url = f"https://api1.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        res = requests.get(url, timeout=3).json()
        price = float(res['lastPrice'])
        change = float(res['priceChangePercent'])
        
        # Lógica de Score simplificada para asegurar carga
        score = 50 + (change * 2) 
        score = np.clip(score, 10, 95)
        st.session_state.score_mem[symbol] = score
        
        trend = "UP" if change > 0 else "DOWN"
        return price, score, trend
    except:
        return None, st.session_state.score_mem[symbol], "WAIT"

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER PRO</h1>", unsafe_allow_html=True)

cols = st.columns(3)

for i, sym in enumerate(PAIRS):
    price, score, trend = get_data(sym)
    
    with cols[i % 3]:
        display_price = f"${price:,.2f}" if price else "Sincronizando..."
        t_color = "#00ff88" if score >= THRESHOLD else "#00fbff"
        
        st.markdown(f"""
            <div class="crypto-card">
                <div class="pair-name">{sym}</div>
                <div class="live-price">{display_price}</div>
                <div style="color:{t_color}; font-size:20px; font-weight:bold; margin-top:5px;">
                    SCORE: {score:.1f}
                </div>
                <div style="color:white; font-size:12px;">TENDENCIA: {trend}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Gráfico Radar con KEY ÚNICA para evitar el error DuplicateElementId
        fig = go.Figure(go.Scatterpolar(
            r=[score, 60, 70, 50, 80, score],
            theta=['A','B','C','D','E','A'],
            fill='toself', line=dict(color=t_color)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            showlegend=False, height=150, paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20,r=20,t=10,b=10)
        )
        # Aquí está la corrección: key=f"chart_{sym}"
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{sym}")
