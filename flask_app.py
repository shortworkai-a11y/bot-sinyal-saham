from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

# Daftar saham (Watchlist) - Gunakan jumlah sedikit dulu untuk memastikan kecepatan server
WATCHLIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 
    'BBNI.JK', 'UNTR.JK', 'GOTO.JK', 'AMRT.JK', 'ADRO.JK'
]

def get_signals():
    data_list = []
    
    # Headers agar tidak diblokir oleh Yahoo Finance (Bot Protection)
    for ticker in WATCHLIST:
        try:
            # Menggunakan yf.download karena lebih stabil di server cloud
            # period '5d' untuk efisiensi data
            df = yf.download(ticker, period='5d', interval='1h', progress=False, threads=False)
            
            if df.empty or len(df) < 2:
                continue
                
            last_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change = ((last_price - prev_price) / prev_price) * 100
            
            # Logika Sederhana: Buy jika harga di atas rata-rata 5 hari
            avg_price = df['Close'].mean()
            if last_price > avg_price:
                signal = "BUY"
            elif last_price < avg_price:
                signal = "SELL"
            else:
                signal = "NEUTRAL"
                
            data_list.append({
                'ticker': ticker.replace('.JK', ''),
                'price': f"{last_price:,.0f}",
                'change': round(change, 2),
                'signal': signal
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue
            
    return data_list

@app.route('/')
def index():
    # Flask akan otomatis mencari folder 'templates' di direktori yang sama
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    signals = get_signals()
    return jsonify(signals)

if __name__ == '__main__':
    app.run(debug=True)
