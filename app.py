from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Daftar saham (Tanpa .JK di tampilan, tapi ditambahkan saat fetch)
WATCHLIST = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO', 'ADRO', 'BBNI']

def get_signal_logic(change):
    if change > 1.5: return "STRONG BUY"
    if change > 0: return "BUY"
    if change < -1.5: return "STRONG SELL"
    if change < 0: return "SELL"
    return "NEUTRAL"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    data_list = []
    try:
        # Ambil data sekaligus (bulk download) agar lebih cepat & aman dari blokir
        tickers_jk = [f"{t}.JK" for t in WATCHLIST]
        # Menggunakan period 2d untuk mendapatkan data hari ini dan kemarin
        data = yf.download(tickers_jk, period="2d", interval="1d", group_by='ticker', progress=False)
        
        for ticker in WATCHLIST:
            try:
                ticker_data = data[f"{ticker}.JK"]
                if len(ticker_data) >= 2:
                    last_price = float(ticker_data['Close'].iloc[-1])
                    prev_close = float(ticker_data['Close'].iloc[-2])
                    
                    # Hitung persentase
                    change = ((last_price - prev_close) / prev_close) * 100
                    
                    data_list.append({
                        'ticker': ticker,
                        'price': f"{last_price:,.0f}",
                        'change': round(change, 2),
                        'signal': get_signal_logic(change)
                    })
            except:
                continue
    except Exception as e:
        print(f"Error: {e}")
        
    return jsonify(data_list)

if __name__ == '__main__':
    app.run()
