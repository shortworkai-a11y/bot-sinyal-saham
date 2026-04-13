from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

# Daftar saham terbatas untuk memastikan server gratisan tidak overload
WATCHLIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 
    'BBNI.JK', 'UNTR.JK', 'GOTO.JK', 'AMRT.JK', 'ADRO.JK'
]

def get_signals():
    data_list = []
    for ticker in WATCHLIST:
        try:
            # Menggunakan period '5d' agar lebih ringan tapi data MA/RSI tetap valid
            stock = yf.Ticker(ticker)
            df = stock.history(period='5d', interval='1h')
            
            if df.empty:
                continue
                
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change = ((last_price - prev_price) / prev_price) * 100
            
            # Logika Sederhana Predator (Contoh: Trend)
            signal = "NEUTRAL"
            if last_price > df['Close'].mean():
                signal = "BUY"
            elif last_price < df['Close'].mean():
                signal = "SELL"
                
            data_list.append({
                'ticker': ticker.replace('.JK', ''),
                'price': round(last_price, 2),
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
    return jsonify(signals)

if __name__ == '__main__':
    app.run(debug=True)
