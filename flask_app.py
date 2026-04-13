from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import requests

app = Flask(__name__)

# Gunakan 2 saham paling stabil saja dulu untuk 'pemanasan' koneksi server
WATCHLIST = ['BBCA.JK', 'BBRI.JK']

def get_signals():
    data_list = []
    
    # Bypass Headers (Meniru browser Chrome asli)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for ticker in WATCHLIST:
        try:
            # Gunakan session requests agar Yahoo tidak curiga
            session = requests.Session()
            session.headers.update(headers)
            
            stock = yf.Ticker(ticker, session=session)
            
            # AMBIL DATA PALING RINGAN (1 hari terakhir, interval 30m)
            df = stock.history(period='1d', interval='30m')
            
            if df.empty or len(df) < 1:
                # Jika 1d gagal, coba ambil 5d sebagai cadangan
                df = stock.history(period='5d', interval='1d')
            
            if not df.empty:
                last_price = float(df['Close'].iloc[-1])
                # Hitung perubahan dari harga closing kemarin
                if len(df) > 1:
                    prev_close = float(df['Close'].iloc[-2])
                else:
                    prev_close = last_price # Fallback jika data cuma 1
                
                change = ((last_price - prev_close) / prev_close) * 100
                
                # Logika Sinyal Sederhana
                signal = "BUY" if change > 0 else "SELL"
                if abs(change) < 0.1: signal = "NEUTRAL"

                data_list.append({
                    'ticker': ticker.replace('.JK', ''),
                    'price': f"{last_price:,.0f}",
                    'change': round(change, 2),
                    'signal': signal
                })
        except Exception as e:
            print(f"Error {ticker}: {e}")
            continue
            
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    signals = get_signals()
    # Jika masih kosong, jangan kirim ERROR, tapi kirim status WAITING
    if not signals:
        return jsonify([{"ticker": "WAITING", "price": "SYNC", "change": 0, "signal": "RECONNECTING"}]), 200
    return jsonify(signals)

if __name__ == '__main__':
    app.run(debug=True)
