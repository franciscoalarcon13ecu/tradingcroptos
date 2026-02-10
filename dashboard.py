import streamlit as st, requests, pandas as pd, numpy as np, plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st_autorefresh(interval=5000, key="f_emergency_v2")

# CSS Minimalista para noche oscura
st.markdown("<style>body{background-color:#06090f;color:white;}</style>", unsafe_allow_html=True)

def get_data(s):
    try:
        # Usamos FAPI (Futuros) en lugar de API (Spot) para saltar el bloqueo de IP
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}"
        r = requests.get(url, timeout=2).json()
        return float(r['price'])
    except: 
        return 0.0

st.title("🏹 SNIPER EMERGENCY MODE (FAPI)")

cols = st.columns(3)
pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]

for i, p in enumerate(pairs):
    price = get_data(p)
    with cols[i%3]:
        # Si el precio sigue en 0, mostramos un mensaje de "Bloqueo de Red"
        display_val = f"${price:,.2f}" if price > 0 else "RED BLOQUEADA"
        st.metric(label=p, value=display_val)
        
        # Radar simple para ver si el motor gráfico vive
        fig = go.Figure(go.Scatterpolar(r=[price%100, 50, 70, 40, 50, price%100], 
            theta=['VOL','CVD','RSI','MOM','SCORE','VOL'], fill='toself'))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            height=200, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"radar_{p}")
