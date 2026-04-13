import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# 1. PREMIUM INTERFACE CONFIG
# ==========================================
st.set_page_config(page_title="PRO-QUANT v15 | INSTITUTIONAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { 
        background-color: #020202; font-family: 'JetBrains Mono', monospace; color: #e0e0e0;
    }
    header, footer { visibility: hidden; }
    .status-bar { 
        background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
        padding: 12px; border-bottom: 2px solid #00ff9d; 
        margin-bottom: 10px; display: flex; justify-content: space-between;
        border-radius: 5px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    [data-testid="stMetric"] { background: #0a0a0a; border-left: 3px solid #00ff9d; padding: 10px; border-radius: 4px; }
    .segment-header { font-size: 18px; font-weight: bold; color: #00d4ff; padding: 10px 0; border-bottom: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. PLACEHOLDERS (ANTI-DUPLICATE)
# ==========================================
header_ui = st.empty()
m1, m2, m3, m4 = st.columns(4)
metric_1, metric_2, metric_3, metric_4 = m1.empty(), m2.empty(), m3.empty(), m4.empty()
st.divider()
table_container = st.container()

# ==========================================
# 3. CORE ANALYZER FUNCTION
# ==========================================
watchlist = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'ASII.JK', 'TLKM.JK', 'GOTO.JK', 
    'ANTM.JK', 'BRMS.JK', 'ADRO.JK', 'PTBA.JK', 'AMMN.JK', 'MEDC.JK', 'MDKA.JK', 
    'BRIS.JK', 'MBMA.JK', 'ACES.JK', 'RAJA.JK', 'DOID.JK', 'NCKL.JK', 'TPIA.JK',
    'BULL.JK', 'LSIP.JK', 'CPIN.JK', 'UNTR.JK', 'AKRA.JK', 'INKP.JK', 'SMGR.JK'
]

@st.cache_data(ttl=3600) # Fundamental data di-cache 1 jam agar cepat
def get_fundamental_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        return {
            'PE': info.get('trailingPE', 999),
            'PBV': info.get('priceToBook', 999),
            'ROE': info.get('returnOnEquity', 0) * 100,
            'DER': info.get('debtToEquity', 999) / 100,
            'NI_Growth': info.get('netIncomeToCommon', 0), # Simplified YoY
            'OCF': info.get('operatingCashflow', 0)
        }
    except:
        return {'PE': 999, 'PBV': 999, 'ROE': 0, 'DER': 999, 'NI_Growth': 0, 'OCF': 0}

@st.cache_data(ttl=1)
def fetch_live_prices():
    return yf.download(watchlist + ['GC=F', '^JKSE'], period="5d", interval="1d", group_by='ticker', progress=False)

# ==========================================
# 4. EXECUTION LOOP
# ==========================================
while True:
    live_data = fetch_live_prices()
    
    # --- UPDATE TOP BAR ---
    with header_ui:
        gold = live_data['GC=F']['Close'].iloc[-1]
        ihsg = live_data['^JKSE']['Close'].iloc[-1]
        ihsg_c = ((ihsg - live_data['^JKSE']['Close'].iloc[-2]) / live_data['^JKSE']['Close'].iloc[-2]) * 100
        st.markdown(f"""
        <div class="status-bar">
            <span style="font-weight:bold; letter-spacing:1px;">🛡️ PRO-QUANT v15.0 | INSTITUTIONAL ANALYZER</span>
            <span>IHSG: {ihsg:,.0f} ({ihsg_c:+.2f}%) | XAUUSD: ${gold:,.2f}</span>
            <span style="color:#00ff9d;">● LIVE {datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        """, unsafe_allow_html=True)

    processed_rows = []
    for t in watchlist:
        try:
            df = live_data[t].dropna()
            c, p_c, h, l, o, v = df['Close'].iloc[-1], df['Close'].iloc[-2], df['High'].iloc[-1], df['Low'].iloc[-1], df['Open'].iloc[-1], df['Volume'].iloc[-1]
            v_avg = df['Volume'].tail(15).mean()
            
            # Technical Metrics
            chg = ((c - p_c) / p_c) * 100
            vr = v / (v_avg + 1)
            dist_h = (1 - (c / h)) * 100
            
            # Fundamental Metrics (Cached)
            f = get_fundamental_data(t)
            
            # 1. Segmentasi
            segment = "SMALL" if c < 300 else "MID" if c < 2000 else "BIG"
            
            # Fundamental Filtering (Scoring)
            f_score = 0
            if f['PE'] < 12: f_score += 1
            if f['PBV'] < 1.5: f_score += 1
            if f['ROE'] > 12: f_score += 1
            if f['DER'] < 1: f_score += 1
            if f['OCF'] > 0: f_score += 1

            # 2. Signal Logic (BSJP & BPJS)
            sig = "-"
            score = 0
            if chg > 1.8 and dist_h < 0.003 and vr > 1.5:
                sig = "🔥 BSJP"
                score = 5
            elif ((o-p_c)/p_c) > 0.005 and c > o:
                sig = "⚡ BPJS"
                score = 4
            elif vr > 2.5:
                sig = "🐋 WHALE"
                score = 3

            processed_rows.append({
                'SEGMENT': segment,
                'TICKER': t.replace('.JK',''),
                'LAST': int(c),
                'CHG%': round(chg, 2),
                'V-R': round(vr, 1),
                'PE': round(f['PE'], 1),
                'PBV': round(f['PBV'], 1),
                'ROE%': round(f['ROE'], 1),
                'DER': round(f['DER'], 2),
                'SIGNAL': sig,
                'F_SCORE': f_score,
                'RANK': score
            })
        except: continue

    df_main = pd.DataFrame(processed_rows)

    # --- UPDATE METRICS ---
    metric_1.metric("TOTAL ASSETS", len(df_main))
    metric_2.metric("BSJP SIGNAL", len(df_main[df_main['RANK'] == 5]))
    metric_3.metric("VALUE STOCKS", len(df_main[df_main['F_SCORE'] >= 4]))
    metric_4.metric("BIG CAP ACTIVE", len(df_main[(df_main['SEGMENT'] == 'BIG') & (df_main['CHG%'] > 0)]))

    # --- UPDATE TABLE PER SEGMENT ---
    with table_container:
        for seg in ["BIG", "MID", "SMALL"]:
            st.markdown(f"<div class='segment-header'>{seg} CAP SEGMENT</div>", unsafe_allow_html=True)
            df_seg = df_main[df_main['SEGMENT'] == seg].sort_values(['RANK', 'CHG%'], ascending=[False, False])
            
            st.dataframe(
                df_seg.drop(columns=['SEGMENT', 'RANK']).style.applymap(
                    lambda x: f'color: {"#00ff9d" if x > 0 else "#ff3131" if x < 0 else "#888"}; font-weight: bold;', 
                    subset=['CHG%', 'ROE%']
                ).applymap(
                    lambda x: 'background-color: #004d1a; color: white;' if "BSJP" in str(x) else 
                               'background-color: #002b4d; color: white;' if "BPJS" in str(x) else '', 
                    subset=['SIGNAL']
                ).applymap(
                    lambda x: 'color: #f1c40f; font-weight: bold;' if x >= 4 else '', subset=['F_SCORE']
                ),
                use_container_width=True
            )

    time.sleep(1)
