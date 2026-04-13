import pandas as pd
import requests
from io import StringIO
from flask import Flask, jsonify, render_template
import os

# Inisialisasi Flask dengan mengarahkan folder template ke luar folder api
app = Flask(__name__, template_folder='../templates')

# PASTE LINK CSV HASIL PUBLISH TO WEB DI SINI
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQye0iX3Sh2qkrb8WIfk_IEyE6DKITI_r8y6yOJN0lmT6ggyA1-IgFzmL7dJ2aedNjgm-n2wmm34Egc/pub?output=csv"

def fetch_and_clean_data():
    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        
        final_data = []
        for _, row in df.iterrows():
            try:
                ticker = str(row.get('Ticker', 'N/A'))
                price = float(row.get('Price', 0))
                # Menangani format persen jika Google Sheets mengirim string "0.5%"
                change_raw = str(row.get('Change%', '0')).replace('%', '')
                change_pct = float(change_raw)
                
                pe = float(row.get('PE', 0))
                vol = float(row.get('Volume', 0))
                avg_vol = float(row.get('Avgvolume', 0))
                
                # Logika Sinyal
                score = 0
                if vol > avg_vol and avg_vol > 0: score += 2
                if 0 < pe < 15: score += 3
                
                status = "STRONG BUY" if score >= 4 else "WATCHLIST" if score >= 2 else "NEUTRAL"

                final_data.append({
                    'ticker': ticker,
                    'price': f"{price:,.0f}",
                    'change': f"{change_pct:+.2f}%",
                    'pe': f"{pe:.1f}",
                    'vol_status': "High" if vol > avg_vol else "Normal",
                    'status': status
                })
            except:
                continue
        return final_data
    except Exception as e:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def get_signals():
    data = fetch_and_clean_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Gagal sinkronisasi data"}), 500
