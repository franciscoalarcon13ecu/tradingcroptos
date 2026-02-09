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
st_autorefresh(interval=4000, key="binance_full_data")

# Memoria para el Score (para que no desaparezca si hay lag)
if 'score_mem' not in st.session_state:
    st.session_state.score_mem = {pair: 50.0 for pair in PAIRS}

# Estilo CSS
st.markdown("""
    <style>
    .stApp { background-color: #06090f; }
    .crypto-card {
        background: rgba(16, 22, 35, 0.9);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 251, 255, 0.2);
        margin-bottom: 10px;
    }
    .pair-name { color: #00fbff; font-weight: bold; font-size: 16px; }
    .live-price { color: #ffffff; font-family: 'Courier New', monospace; font-size: 26px; font-weight: bold; }
    .score-text { font-size: 20px; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

def get_full_data(symbol):
    try:
        # 1. Obtener Precio Actual
        p_res = requests.get(f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=2).json()
        price = float(p_res['price'])
        
        # 2. Obtener Datos Históricos (Klines) para el Score
        k_res = requests.get(f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=20", timeout=2).json()
        df = pd.DataFrame(k_res, columns=["ot","open","high","low","close","vol","ct","qv","tr","tbb","tbq","i"]).apply(pd.to_numeric)
        
        # 3. Cálculo del Score (Volumen + Tendencia)
        v_mean = df['vol'].mean()
        v_last = df['vol'].iloc[-1]
        trend = "UP" if price > df['open'].iloc[-1] else "DOWN"
        
        # Lógica del Score
        score = 50 + (15 if v_last > v_mean else -5) + (15 if trend == "UP" else -15)
        st.session_state.score_mem[symbol] = score # Guardar en memoria
        
        return price, score, trend
    except:
        # Si falla la conexión, devuelve lo último que tenemos
        return None, st.session_state.score_mem[symbol], "WAIT"

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER PRO</h1>", unsafe_allow_html=True)

cols = st.columns(3)

for i, sym in enumerate(PAIRS):
    price, score, trend = get_full_data(sym)
    
    with cols[i % 3]:
        # Si el precio es None, usamos un precio genérico de carga
        display_price = f"${price:,.2f}" if price else "Cargando..."
        t_color = "#00ff88" if score >= THRESHOLD else "#ff4b4b" if score < 40 else "#00fbff"
        
        st.markdown(f"""
            <div class="crypto-card">
                <span class="pair-name">{sym}</span>
                <div class="live-price">{display_price}</div>
                <div class="score-text" style="color:{t_color};">SCORE: {score:.1f}</div>
                <div style="color:white; font-size:12px;">TENDENCIA: {trend}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Gráfico Radar con el Score real
        fig = go.Figure(go.Scatterpolar(
            r=[score, 60, 70, score-10, 80, score],
            theta=['SCORE','VOL','RSI','MOM','TREND','SCORE'],
            fill='toself', line=dict(color=t_color)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            showlegend=False, height=150, paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20,r=20,t=20,b=20)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
