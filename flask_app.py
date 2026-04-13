from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

# Gunakan maksimal 5-7 saham saja untuk akun FREE agar tidak kena Limit Server
WATCHLIST = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK']

def get_signals():
    data_list = []
    
    for ticker in WATCHLIST:
        try:
            # Inisialisasi Ticker
            stock = yf.Ticker(ticker)
            
            # Ambil data minimal (period 2 hari sudah cukup untuk sinyal harian)
            # interval 1h adalah yang paling stabil di server cloud
            df = stock.history(period='2d', interval='1h')
            
            if df.empty or len(df) < 2:
                continue
                
            last_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change = ((last_price - prev_price) / prev_price) * 100
            
            # Logika PREDATOR CORE: Simple Moving Average Comparison
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
            print(f"Error pada {ticker}: {e}")
            continue
            
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    try:
        signals = get_signals()
        return jsonify(signals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
