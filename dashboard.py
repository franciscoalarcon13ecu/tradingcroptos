import streamlit as st, requests, pandas as pd, numpy as np, plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st_autorefresh(interval=5000, key="f")

# CSS Minimalista
st.markdown("<style>body{background-color:#06090f;color:white;}</style>", unsafe_allow_html=True)

def get_data(s):
    try:
        url = f"https://api1.binance.com/api/v3/ticker/price?symbol={s}"
        r = requests.get(url, timeout=2).json()
        return float(r['price'])
    except: return 0.0

st.title("🏹 SNIPER EMERGENCY MODE")

cols = st.columns(3)
pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]

for i, p in enumerate(pairs):
    price = get_data(p)
    with cols[i%3]:
        st.metric(label=p, value=f"${price:,.2f}")
        # Radar simple
        fig = go.Figure(go.Scatterpolar(r=[price%100, 50, 70, 40, 50, price%100], 
            theta=['A','B','C','D','E','A'], fill='toself'))
        fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False}, key=p)
