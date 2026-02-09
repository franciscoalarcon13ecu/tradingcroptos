import streamlit as st
from supabase import create_client
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- CONFIG ---
st.set_page_config(page_title="QUANTUM SNIPER LIVE", layout="wide")
st_autorefresh(interval=3000, key="bridge_refresh")

SUPABASE_URL = "https://gjcmfmaawnlhsihcyptp.supabase.co"
SUPABASE_KEY = "TU_ANON_KEY_DE_SUPABASE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Estilo Negro Original
st.markdown("<style>.stApp { background-color: #06090f; }</style>", unsafe_allow_True=True)

def load_data():
    res = supabase.table("sniper_bridge").select("*").execute()
    return res.data

st.markdown("<h2 style='text-align:center; color:#00fbff;'>🏹 QUANTUM SNIPER (LIVE SYNC)</h2>", unsafe_allow_html=True)

data = load_data()
if data:
    cols = st.columns(3)
    for i, row in enumerate(data):
        with cols[i % 3]:
            st.markdown(f"""
                <div style="background:rgba(16,22,35,0.9); border:1px solid #00fbff; padding:15px; border-radius:10px; text-align:center;">
                    <h3 style="color:#00fbff; margin:0;">{row['symbol']}</h3>
                    <h2 style="color:white; margin:10px 0;">${row['price']:,.2f}</h2>
                    <h3 style="color:#00ff88;">SCORE: {row['score']}</h3>
                    <p style="color:gray;">TENDENCIA: {row['trend']}</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Esperando señal desde la estación base (Tu PC)...")
