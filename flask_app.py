from flask import Flask, render_template, jsonify
import requests
import pandas as pd
import os

app = Flask(__name__)

# List Saham Pilihan
WATCHLIST = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO']

def get_signals():
    data_list = []
    
    for ticker in WATCHLIST:
        try:
            # Menggunakan API publik alternatif yang lebih stabil untuk data IHSG
            # Kita mengambil data dari penyedia data pasar yang mendukung CORS/Cloud
            url = f"https://api.goapi.io/stock/idx/{ticker}/latest?api_key=FREE_TRIAL_KEY" 
            # Note: Gunakan yfinance kembali dengan optimasi header jika API di atas limit
            
            import yfinance as yf
            stock = yf.Ticker(f"{ticker}.JK")
            df = stock.history(period='2d', interval='1h')
            
            if df.empty:
                continue
                
            last_price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change = ((last_price - prev_close) / prev_close) * 100
            
            # Algoritma Predator: Price Action + Trend
            avg_price = df['Close'].mean()
            if last_price > avg_price and change > 0:
                signal = "STRONG BUY"
            elif last_price > avg_price:
                signal = "BUY"
            elif last_price < avg_price:
                signal = "SELL"
            else:
                signal = "NEUTRAL"
                
            data_list.append({
                'ticker': ticker,
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
    return jsonify(get_signals())

if __name__ == '__main__':
    app.run(debug=True)
