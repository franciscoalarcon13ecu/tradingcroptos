import os, requests, numpy as np, pandas as pd, streamlit as st, plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. CONFIGURACIÓN INICIAL
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
LOG_FILE = "backtest_log.csv"

st.set_page_config(page_title="QUANTUM SNIPER", layout="wide")

# Actualización cada 5 segundos
st_autorefresh(interval=5000, key="quantum_refresh_v23")

# 2. ESTILO VISUAL (CSS)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #06090f; }
    .crypto-card {
        background-color: #101623;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #1d2636;
        text-align: center;
        margin-bottom: 10px;
    }
    .price-val { color: #ffffff; font-size: 32px; font-weight: bold; margin: 10px 0; }
    .pair-name { color: #00fbff; font-size: 18px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LOCAL (Log)
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["timestamp", "symbol", "price", "score", "trend"]).to_csv(LOG_FILE, index=False)

def fetch_data(symbol):
    # Usamos la API de VISION que es la más estable para Streamlit Cloud
    urls = [
        f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=1m&limit=30",
        f"https://api3.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=30"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                data = res.json()
                df = pd.DataFrame(data).apply(pd.to_numeric)
                curr_price = df[4].iloc[-1]
                v_smooth = df[5].iloc[-3:].mean()
                v_mean = df[5].mean()
                z_vol = (v_smooth - v_mean) / (df[5].std() + 1e-9)
                score = 50 + (np.clip(abs(z_vol), 0, 2.5) * 15)
                trend = "UP" if curr_price > df[1].iloc[-1] else "DOWN"
                
                # Métricas para el Radar
                metrics = [
                    round(score, 1), 
                    round(50 + (z_vol * 10), 1), 
                    60, 
                    round(50 + (abs(z_vol) * 12), 1), 
                    85 if trend == "UP" else 15
                ]
                return curr_price, score, trend, metrics
        except:
            continue
    return 0.0, 50.0, "ESPERANDO", [50, 50, 50, 50, 50]

# 4. INTERFAZ DE USUARIO
st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER LIVE</h1>", unsafe_allow_html=True)

cols = st.columns(3)
for i, sym in enumerate(PAIRS):
    price, score, trend, metrics = fetch_data(sym)
    color = "#00ff88" if trend == "UP" else "#ff4b4b"
    
    with cols[i % 3]:
        # Tarjeta de Precio
        st.markdown(f"""
            <div class="crypto-card">
                <div class="pair-name">{sym}</div>
                <div class="price-val">${price:,.2f}</div>
                <div style="color:{color}; font-weight:bold;">SCORE: {score:.1f} | {trend}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Gráfico de Radar
        fig = go.Figure(go.Scatterpolar(
            r=metrics + [metrics[0]],
            theta=['SCORE', 'CVD', 'RSI', 'VOL', 'MOM', 'SCORE'],
            fill='toself', 
            line=dict(color=color, width=2)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(color="#00fbff", size=10), rotation=90),
                domain=dict(x=[0.1, 0.9], y=[0.1, 0.9])
            ),
            showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"radar_{sym}")

# 5. TABLA DE LOGS
st.write("---")
st.subheader("📊 Historial de Mercado")
try:
    log_df = pd.read_csv(LOG_FILE)
    st.dataframe(log_df.tail(10), use_container_width=True)
except:
    st.info("Sincronizando datos con Binance...")
