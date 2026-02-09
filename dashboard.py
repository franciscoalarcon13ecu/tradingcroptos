import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- CONFIG ---
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
THRESHOLD = 75.0

st.set_page_config(page_title="QUANTUM SNIPER 6-CORE", layout="wide")
st_autorefresh(interval=3000, key="binance_ultra_fast") # Cada 3 seg

# Estilo CSS
st.markdown("""
    <style>
    .stApp { background-color: #06090f; }
    .crypto-card {
        background: rgba(16, 22, 35, 0.9);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 251, 255, 0.2);
    }
    .pair-name { color: #00fbff; font-weight: bold; font-size: 16px; }
    .live-price { color: #ffffff; font-family: 'Courier New', monospace; font-size: 26px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_binance_data(symbol):
    # Usamos el endpoint 'api.binance.us' o 'data-api' que suelen estar más abiertos
    urls = [
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=2).json()
            return float(res['price'])
        except:
            continue
    return None

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER (BINANCE LIVE)</h1>", unsafe_allow_html=True)

cols = st.columns(3)

for i, sym in enumerate(PAIRS):
    price = get_binance_data(sym)
    
    with cols[i % 3]:
        if price is None:
            st.error(f"Error conexión {sym}")
            continue
            
        st.markdown(f"""
            <div class="crypto-card">
                <span class="pair-name">{sym}</span>
                <div class="live-price">${price:,.2f}</div>
                <div style="color:#00ff88; font-size:12px; margin-top:5px;">● BINANCE REAL-TIME</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Mini gráfico simulado para no perder el estilo
        metrics = [np.random.randint(60, 90) for _ in range(5)]
        fig = go.Figure(go.Scatterpolar(r=metrics + [metrics[0]], theta=['A','B','C','D','E','A'], fill='toself', line=dict(color='#00fbff')))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=150, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
