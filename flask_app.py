from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

# Gunakan 4 saham saja dulu untuk tes. Jika muncul, baru tambah lagi.
WATCHLIST = ['BBCA.JK', 'BBRI.JK', 'TLKM.JK', 'ASII.JK']

def get_signals():
    data_list = []
    
    # Setup Session agar tidak dianggap bot
    import requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    for ticker in WATCHLIST:
        try:
            # Menggunakan session dan proxy-less fetch
            stock = yf.Ticker(ticker, session=session)
            
            # Ambil data minimal (1 hari terakhir dengan interval 15 menit)
            # Ini jauh lebih ringan dan cepat daripada data harian/mingguan
            df = stock.history(period='1d', interval='15m')
            
            if df.empty or len(df) < 2:
                continue
                
            last_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change = ((last_price - prev_price) / prev_price) * 100
            
            # Algoritma Sederhana: Buy jika harga terakhir > harga pembukaan hari ini
            open_price = float(df['Open'].iloc[0])
            if last_price > open_price:
                signal = "BUY"
            elif last_price < open_price:
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
            print(f"Gagal akses {ticker}: {e}")
            continue
            
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    # Jika hasil fungsi kosong, kirim pesan error yang jelas
    signals = get_signals()
    if not signals:
        return jsonify([{"ticker": "ERROR", "price": "0", "change": 0, "signal": "LIMIT SERVER"}]), 200
    return jsonify(signals)

if __name__ == '__main__':
    app.run(debug=True)
