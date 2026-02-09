import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="QUANTUM SNIPER LIVE", layout="wide")

# Autorefresh cada 2 segundos para sincronizar con tu Mac
st_autorefresh(interval=2000, key="bridge_sync")

# Inicializar Supabase
SUPABASE_URL = "https://gjcmfmaawnlhsihcyptp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqY21mbWFhd25saHNpaGN5cHRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA2NjMwMDgsImV4cCI6MjA4NjIzOTAwOH0.0xJ00mtixyK3KLGgfpcZkEORQGHwR2qy-hVzmYlpMYk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ESTILO VISUAL SNIPER ---
st.markdown("""
    <style>
    .stApp { background-color: #06090f; }
    .card {
        background: rgba(16, 22, 35, 0.9);
        border: 2px solid #00fbff;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .price { color: #ffffff; font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; }
    .score { font-size: 24px; font-weight: bold; margin-top: 10px; }
    .symbol { color: #00fbff; font-size: 18px; font-weight: bold; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER 6-CORE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>DATABASE BRIDGE: ACTIVE CONNECTION</p>", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
try:
    res = supabase.table("sniper_bridge").select("*").execute()
    data = res.data
    
    if data:
        # 🟢 EL TRUCO: Ordenamos alfabéticamente por 'symbol' para que NO SALTEN
        data = sorted(data, key=lambda x: x['symbol'])
        
        cols = st.columns(3)
        for i, row in enumerate(data):
            with cols[i % 3]:
                # Definir color según el Score (Verde si es alto, Rojo si es bajo)
                if row['score'] >= 75:
                    color = "#00ff88"  # Sniper Green
                elif row['score'] <= 35:
                    color = "#ff4b4b"  # Danger Red
                else:
                    color = "#00fbff"  # Neutral Cyan

                st.markdown(f"""
                    <div class="card" style="border-color:{color}; box-shadow: 0px 0px 15px {color}33;">
                        <div class="symbol">{row['symbol']}</div>
                        <div class="price">${row['price']:,.2f}</div>
                        <div class="score" style="color:{color};">SCORE: {row['score']}</div>
                        <div style="color:gray; font-size:10px; margin-top:10px;">TREND: {row.get('trend', 'SCANNING')}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Esperando señal desde la estación base de Francisco...")
        
except Exception as e:
    st.error(f"Error de enlace: {e}")

st.markdown("---")
st.caption("Sistema de transmisión encriptada via Supabase Bridge.")
