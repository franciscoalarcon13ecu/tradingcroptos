import streamlit as st, requests, pandas as pd, numpy as np, plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide")
st_autorefresh(interval=5000, key="resurrection_final_v1")

def get_data(s):
    # Intentamos 3 puertas diferentes en orden de prioridad
    urls = [
        f"https://api.binance.com/api/v3/ticker/price?symbol={s}",
        f"https://api1.binance.com/api/v3/ticker/price?symbol={s}",
        f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}"
    ]
    
    for url in urls:
        try:
            r = requests.get(url, timeout=1.5)
            if r.status_code == 200:
                return float(r.json()['price'])
        except:
            continue
    return 0.0

# --- EL RESTO DEL CÓDIGO (EMERGENCY MODE) ---
st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 SNIPER CLOUD: ESTADO CRÍTICO</h1>", unsafe_allow_html=True)

pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
cols = st.columns(3)

for i, p in enumerate(pairs):
    price = get_data(p)
    with cols[i%3]:
        if price > 0:
            st.metric(label=p, value=f"${price:,.2f}")
        else:
            st.error(f"{p}: SIN CONEXIÓN")
