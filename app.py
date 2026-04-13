import pandas as pd
import requests
from io import StringIO
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# GANTI LINK DI BAWAH INI dengan link yang baru saja Anda dapatkan
SHEET_CSV_URL = "ISI_DENGAN_LINK_CSV_ANDA_DI_SINI"

def fetch_stock_data():
    try:
        # Menarik data dari Google Sheets
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        
        # Membaca CSV menggunakan Pandas
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Membersihkan nama kolom (menghapus spasi jika ada)
        df.columns = df.columns.str.strip()
        
        results = {'small': [], 'mid': [], 'big': []}
        
        # Looping data saham
        for _, row in df.iterrows():
            try:
                # Ambil data dari kolom (sesuaikan nama kolom dengan di Sheets)
                symbol = str(row['Ticker'])
                price = float(row['Price'])
                pe = float(row['PE']) if 'PE' in df.columns else 0
                pbv = float(row['PBV']) if 'PBV' in df.columns else 0
                
                # Logika Skor Sederhana (Contoh: Berdasarkan PE)
                score = 0
                if pe > 0 and pe < 15: score += 3
                if pbv > 0 and pbv < 1.5: score += 2
                
                stock_info = {
                    'symbol': symbol,
                    'price': f"{price:,.0f}",
                    'pe': pe,
                    'pbv': pbv,
                    'score': score,
                    'status': "SOVEREIGN" if score >= 4 else "NEUTRAL"
                }
                
                # Klasifikasi berdasarkan harga (Contoh saja)
                if price < 500:
                    results['small'].append(stock_info)
                elif price < 5000:
                    results['mid'].append(stock_info)
                else:
                    results['big'].append(stock_info)
            except Exception as e:
                print(f"Error baris {symbol}: {e}")
                continue
                
        return results
    except Exception as e:
        print(f"Error Global: {e}")
        return None

@app.route('/api/signals')
def get_signals():
    data = fetch_stock_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Gagal mengambil data dari Google Sheets"}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
