import os, requests, numpy as np, pandas as pd, streamlit as st, plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# CONFIG
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
LOG_FILE = "backtest_log.csv"

st.set_page_config(page_title="QUANTUM SNIPER", layout="wide")
st_autorefresh(interval=5000, key="quantum_v19")

# Crear log si no existe
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["timestamp", "symbol", "price", "score", "trend", "clv", "cvd", "rsi", "vol", "mom"]).to_csv(LOG_FILE, index=False)

def fetch_data(symbol):
    try:
        # Usamos api3 para evitar bloqueos en el link de internet
        url = f"https://api3.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=30"
        res = requests.get(url, timeout=2).json()
        df = pd.DataFrame(res).apply(pd.to_numeric)
        
        curr_price = df[4].iloc[-1]
        v_smooth, v_mean = df[5].iloc[-3:].mean(), df[5].mean()
        z_vol = (v_smooth - v_mean) / (df[5].std() + 1e-9)
        score = 50 + (np.clip(abs(z_vol), 0, 2.5) * 15)
        trend = "UP" if curr_price > df[1].iloc[-1] else "DOWN"
        
        # --- ESTO ES LO QUE HACE QUE LA TERMINAL SE MUEVA ---
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Sincronizando {symbol}: ${curr_price} | Score: {score:.1f}")
        # ---------------------------------------------------

        metrics = [round(score,1), round(50+(z_vol*10),1), 60, round(50+(abs(z_vol)*12),1), 85 if trend=="UP" else 15]
        return curr_price, score, trend, metrics
    except Exception as e:
        print(f"❌ Error en {symbol}: {e}")
        return 0.0, 50.0, "API WAIT", [50, 50, 50, 50, 50]

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER LIVE</h1>", unsafe_allow_html=True)

cols = st.columns(3)
for i, sym in enumerate(PAIRS):
    price, score, trend, metrics = fetch_data(sym)
    color = "#00ff88" if score > 70 and trend == "UP" else "#ff4b4b" if score > 70 else "#00fbff"
    
    with cols[i % 3]:
        st.markdown(f'''
            <div style="background:#101623; border:1px solid {color}; border-radius:10px; padding:15px; margin-bottom:10px;">
                <h3 style="margin:0;color:#00fbff;">{sym}</h3>
                <h2 style="margin:0;color:white;">${price:,.2f}</h2>
                <p style="margin:0;color:{color}; font-weight:bold;">SCORE: {score:.1f} | {trend}</p>
            </div>''', unsafe_allow_html=True)
        
        fig = go.Figure(go.Scatterpolar(r=metrics+[metrics[0]], theta=['SC','CVD','RSI','VOL','MOM','SC'], fill='toself', line=dict(color=color)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), angularaxis=dict(tickfont=dict(color="#00fbff", size=10), rotation=90), domain=dict(x=[0.15, 0.85], y=[0.15, 0.85])),
                          showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch', key=f"web_{sym}_{i}")

st.write("---")
st.subheader("📊 Historial de Señales")
log_df = pd.read_csv(LOG_FILE)
st.dataframe(log_df.tail(10), width='stretch')
