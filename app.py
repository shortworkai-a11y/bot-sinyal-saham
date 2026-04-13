from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Daftar saham pilihan
WATCHLIST = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO', 'ADRO', 'BBNI']

def get_market_data():
    data_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    for ticker in WATCHLIST:
        try:
            # Mengambil data dari API Sectors.app
            url = f"https://sectors.app/api/stock/daily/{ticker}/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                raw_data = response.json()
                
                # Menangani format list atau dictionary
                if isinstance(raw_data, list) and len(raw_data) > 0:
                    latest = raw_data[-1]
                elif isinstance(raw_data, dict) and 'data' in raw_data:
                    latest = raw_data['data'][-1]
                else:
                    continue

                last_price = float(latest.get('close', 0))
                prev_price = float(latest.get('prev_close', 0))
                
                # Hitung Perubahan Harga
                change = ((last_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                
                # Logika Sinyal Predator
                if change > 1.5: signal = "STRONG BUY"
                elif change > 0: signal = "BUY"
                elif change < -1.5: signal = "STRONG SELL"
                elif change < 0: signal = "SELL"
                else: signal = "NEUTRAL"

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
    return jsonify(get_market_data())

if __name__ == '__main__':
    app.run()
