import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="QUANTUM SNIPER LIVE", layout="wide")

# Forzamos refresco cada 2 segundos para sincronía total
st_autorefresh(interval=2000, key="bridge_sync")

# Inicializar Supabase (El puente con tu PC)
SUPABASE_URL = "https://gjcmfmaawnlhsihcyptp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqY21mbWFhd25saHNpaGN5cHRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA2NjMwMDgsImV4cCI6MjA4NjIzOTAwOH0.0xJ00mtixyK3KLGgfpcZkEORQGHwR2qy-hVzmYlpMYk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. ORDEN SOLICITADO
ORDERED_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .main { background-color: #06090f; color: #ffffff; }
    .crypto-card {
        background: rgba(16, 22, 35, 0.9);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 251, 255, 0.2);
        margin-bottom: 10px;
    }
    .sniper-alert { border: 2px solid #00ff88 !important; box-shadow: 0 0 15px rgba(0, 255, 136, 0.3); }
    .pair-name { color: #00fbff; font-weight: bold; font-size: 16px; letter-spacing: 1px; }
    .live-price { color: #ffffff; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center; color:#00fbff; margin-top:-30px;'>🏹 QUANTUM SNIPER 6-CORE</h2>", unsafe_allow_html=True)

try:
    # LEER DE SUPABASE (Los datos que envía tu PC)
    res = supabase.table("sniper_bridge").select("*").execute()
    raw_data = res.data
    
    if raw_data:
        # Convertir a diccionario para reordenar fácilmente
        data_dict = {row['symbol']: row for row in raw_data}
        
        cols = st.columns(3)
        
        # 2. SEGUIR EL ORDEN ESTRICTO
        for i, sym in enumerate(ORDERED_PAIRS):
            if sym in data_dict:
                row = data_dict[sym]
                price = row['price']
                score = row['score']
                trend = row.get('trend', 'SCANNING')
                metrics = row.get('metrics', [50, 50, 50, 50, 50])
                
                with cols[i % 3]:
                    is_sniper = score >= 75.0
                    t_color = "#00ff88" if is_sniper else "#00fbff"
                    
                    st.markdown(f"""
                        <div class="crypto-card {'sniper-alert' if is_sniper else ''}">
                            <div style="display:flex; justify-content:space-between;">
                                <span class="pair-name">{sym}</span>
                                <span style="color:gray; font-size:10px;">PC SYNC ACTIVE</span>
                            </div>
                            <div class="live-price">${price:,.2f}</div>
                            <div style="display:flex; justify-content:space-between; margin-top:10px; border-top:1px solid #222; padding-top:5px;">
                                <div style="color:{t_color}; font-size:20px; font-weight:bold;">SC: {score:.1f}</div>
                                <div style="color:white; font-weight:bold;">{trend}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Gráfico Radar con los datos de TU PC
                    fig = go.Figure(go.Scatterpolar(
                        r=metrics + [metrics[0]],
                        theta=['CLV', 'CVD', 'RSI', 'RVOL', 'MOM', 'CLV'],
                        fill='toself', fillcolor=f'rgba(0, 251, 255, 0.1)',
                        line=dict(color=t_color, width=2)
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=False, range=[0, 100]),
                            angularaxis=dict(tickfont=dict(size=10, color="#00fbff"))
                        ),
                        showlegend=False, height=150, margin=dict(l=40, r=40, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Aguardando datos de la estación base...")

except Exception as e:
    st.error(f"Error de conexión: {e}")
