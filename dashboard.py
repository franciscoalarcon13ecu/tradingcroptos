import streamlit as st
from supabase import create_client
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# Esto obliga a Chrome a pedir datos nuevos cada 2 segundos
st_autorefresh(interval=2000, key="frequence_check")

# ... resto del código de Supabase ...

# --- CONFIG ---
st.set_page_config(page_title="QUANTUM SNIPER LIVE", layout="wide")
st_autorefresh(interval=2000, key="bridge_sync")

SUPABASE_URL = "https://gjcmfmaawnlhsihcyptp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqY21mbWFhd25saHNpaGN5cHRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA2NjMwMDgsImV4cCI6MjA4NjIzOTAwOH0.0xJ00mtixyK3KLGgfpcZkEORQGHwR2qy-hVzmYlpMYk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Estilo Negro Sniper
st.markdown("""
    <style>
    .stApp { background-color: #06090f; }
    .card {
        background: rgba(16, 22, 35, 0.9);
        border: 1px solid #00fbff;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    .price { color: #ffffff; font-family: monospace; font-size: 28px; font-weight: bold; }
    .score { font-size: 22px; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER 6-CORE</h1>", unsafe_allow_html=True)

# Leer datos de Supabase
try:
    res = supabase.table("sniper_bridge").select("*").execute()
    data = res.data
    
    if data:
        cols = st.columns(3)
        for i, row in enumerate(data):
            with cols[i % 3]:
                color = "#00ff88" if row['score'] > 70 else "#00fbff"
                st.markdown(f"""
                    <div class="card" style="border-color:{color};">
                        <div style="color:#00fbff; font-weight:bold;">{row['symbol']}</div>
                        <div class="price">${row['price']:,.2f}</div>
                        <div class="score" style="color:{color};">SCORE: {row['score']}</div>
                        <div style="color:gray; font-size:12px; margin-top:5px;">● LIVE BRIDGE ACTIVO</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Esperando datos de la estación base (Francisco PC)...")
except:
    st.error("Error de conexión con el puente.")
