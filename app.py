import pandas as pd
import requests
from io import StringIO
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# PASTE LINK CSV HASIL PUBLISH TO WEB DI SINI
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQye0iX3Sh2qkrb8WIfk_IEyE6DKITI_r8y6yOJN0lmT6ggyA1-IgFzmL7dJ2aedNjgm-n2wmm34Egc/pub?output=csv"

def fetch_and_clean_data():
    try:
        # 1. Ambil data dari Google Sheets
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        
        # 2. Baca CSV ke Pandas DataFrame
        df = pd.read_csv(StringIO(response.text))
        
        # Bersihkan spasi di nama kolom
        df.columns = df.columns.str.strip()
        
        final_data = []
        
        # 3. Looping data 800+ saham
        for _, row in df.iterrows():
            try:
                # Ambil data dasar (Gunakan nilai default 0 jika error/kosong)
                ticker = str(row.get('Ticker', 'N/A'))
                price = float(row.get('Price', 0))
                change_pct = float(row.get('Change%', 0)) * 100 # Konversi ke persen
                pe = float(row.get('PE', 0))
                market_cap = float(row.get('MarketCap', 0))
                vol = float(row.get('Volume', 0))
                avg_vol = float(row.get('Avgvolume', 0))
                
                # LOGIKA SINYAL SOVEREIGN (Contoh sederhana)
                # Sinyal BUY jika Volume > AvgVolume dan PE < 15
                score = 0
                if vol > avg_vol: score += 2
                if pe > 0 and pe < 15: score += 3
                if change_pct > 0: score += 1
                
                status = "STRONG BUY" if score >= 5 else "WATCHLIST" if score >= 3 else "NEUTRAL"

                stock_info = {
                    'ticker': ticker,
                    'price': f"{price:,.0f}",
                    'change': f"{change_pct:+.2f}%",
                    'pe': f"{pe:.1f}",
                    'mcap': f"{market_cap:,.0f}",
                    'vol_status': "High" if vol > avg_vol else "Normal",
                    'score': score,
                    'status': status
                }
                final_data.append(stock_info)
            except:
                continue
                
        return final_data
    except Exception as e:
        print(f"Error Fetching: {e}")
        return None

@app.route('/api/signals')
def get_signals():
    data = fetch_and_clean_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Data tidak ditemukan"}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
