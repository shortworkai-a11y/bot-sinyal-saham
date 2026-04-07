import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# 1. FIXED INTERFACE CONFIG
# ==========================================
st.set_page_config(page_title="PRO-QUANT CORE v13", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { 
        background-color: #050505; font-family: 'JetBrains Mono', monospace; color: #e0e0e0;
    }
    header, footer { visibility: hidden; }
    .status-bar { 
        background: #111; padding: 10px; border-bottom: 2px solid #00ff9d; 
        margin-bottom: 10px; display: flex; justify-content: space-between;
    }
    [data-testid="stMetric"] { background: #0a0a0a; border: 1px solid #222; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DEFINISI WADAH (DI LUAR LOOP)
# ==========================================
# Ini kunci agar UI tidak double: buat wadah kosong SEBELUM loop dimulai
header_ui = st.empty()
m1, m2, m3, m4 = st.columns(4)
metric_1 = m1.empty()
metric_2 = m2.empty()
metric_3 = m3.empty()
metric_4 = m4.empty()
st.divider()
table_ui = st.empty()

# ==========================================
# 3. DATA ENGINE
# ==========================================
watchlist = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'ASII.JK', 'TLKM.JK', 'GOTO.JK', 
    'ANTM.JK', 'BRMS.JK', 'ADRO.JK', 'PTBA.JK', 'AMMN.JK', 'MEDC.JK', 'MDKA.JK', 
    'BRIS.JK', 'MBMA.JK', 'ACES.JK', 'RAJA.JK', 'DOID.JK', 'NCKL.JK', 'TPIA.JK'
]

@st.cache_data(ttl=1)
def fetch_core_data():
    symbols = watchlist + ['GC=F', '^JKSE']
    return yf.download(symbols, period="20d", interval="1d", group_by='ticker', progress=False)

# ==========================================
# 4. EXECUTION LOOP
# ==========================================
while True:
    data = fetch_core_data()
    
    # --- 1. UPDATE HEADER ---
    with header_ui:
        gold = data['GC=F']['Close'].iloc[-1]
        ihsg = data['^JKSE']['Close'].iloc[-1]
        ihsg_c = ((ihsg - data['^JKSE']['Close'].iloc[-2]) / data['^JKSE']['Close'].iloc[-2]) * 100
        st.markdown(f"""
        <div class="status-bar">
            <span style="color:#00ff9d; font-weight:bold;">💎 PRO-QUANT CORE v13.0</span>
            <span>IHSG: {ihsg:,.0f} ({ihsg_c:+.2f}%) | GOLD: ${gold:,.2f}</span>
            <span style="color:#888;">{datetime.now().strftime('%H:%M:%S')} WIB</span>
        </div>
        """, unsafe_allow_html=True)

    # --- 2. DATA PROCESSING ---
    rows = []
    for t in watchlist:
        try:
            df = data[t].dropna()
            c, p_c, h, l, o, v = df['Close'].iloc[-1], df['Close'].iloc[-2], df['High'].iloc[-1], df['Low'].iloc[-1], df['Open'].iloc[-1], df['Volume'].iloc[-1]
            v_avg = df['Volume'].tail(15).mean()
            
            chg = ((c - p_c) / p_c) * 100
            vr = v / (v_avg + 1)
            dist_h = (1 - (c / h)) * 100
            
            sig = "-"
            score = 0
            if chg > 1.5 and dist_h < 0.003 and vr > 1.5:
                sig = "🔥 BSJP CONFIRMED"
                score = 3
            elif vr > 2.5:
                sig = "🐋 WHALE IN"
                score = 2
            elif ((o-p_c)/p_c) > 0.005 and c > o:
                sig = "⚡ BPJS READY"
                score = 2

            rows.append({
                'TICKER': t.replace('.JK',''),
                'LAST': int(c),
                'CHG%': round(chg, 2),
                'V-RATIO': round(vr, 1),
                'SIGNAL': sig,
                'SCORE': score
            })
        except: continue

    df_res = pd.DataFrame(rows).sort_values(['SCORE', 'CHG%'], ascending=[False, False])

    # --- 3. UPDATE METRICS (TETAP DI POSISINYA) ---
    metric_1.metric("BSJP ALERTS", len(df_res[df_res['SCORE'] == 3]))
    metric_2.metric("WHALE ACTIVITY", len(df_res[df_res['SIGNAL'] == "🐋 WHALE IN"]))
    metric_3.metric("MARKET STATUS", "BULLISH" if ihsg_c > 0 else "BEARISH")
    metric_4.metric("SCANNED", len(df_res))

    # --- 4. UPDATE TABLE ---
    with table_ui:
        st.dataframe(
            df_res.style.applymap(lambda x: f'color: {"#00ff9d" if x > 0 else "#ff3131" if x < 0 else "#888"}; font-weight: bold;', subset=['CHG%'])
            .applymap(lambda x: 'background-color: #004d1a; color: white;' if "BSJP" in str(x) else 
                               'background-color: #002b4d; color: white;' if "BPJS" in str(x) else 
                               'background-color: #4d3300; color: white;' if "WHALE" in str(x) else '', subset=['SIGNAL']),
            use_container_width=True, height=800
        )

    time.sleep(1)