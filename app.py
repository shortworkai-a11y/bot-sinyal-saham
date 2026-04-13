from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

WATCHLIST = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO', 'ADRO', 'BBNI']

def get_sectors_data():
    data_list = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for ticker in WATCHLIST:
        try:
            url = f"https://sectors.app/api/stock/daily/{ticker}/"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                raw_data = response.json()
                latest = raw_data[-1] if isinstance(raw_data, list) else raw_data['data'][-1]
                
                last_price = float(latest.get('close', 0))
                prev_price = float(latest.get('prev_close', 0))
                change = ((last_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                
                signal = "BUY" if change > 0 else "SELL"
                if abs(change) < 0.1: signal = "NEUTRAL"

                data_list.append({
                    'ticker': ticker, 
                    'price': f"{last_price:,.0f}",
                    'change': round(change, 2), 
                    'signal': signal
                })
        except: 
            continue
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    return jsonify(get_sectors_data())

# Penting untuk Vercel
if __name__ == '__main__':
    app.run()
