from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Daftar saham (Ticker murni tanpa .JK untuk Sectors.app)
WATCHLIST = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO', 'ADRO', 'BBNI']

def get_sectors_signals():
    data_list = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    for ticker in WATCHLIST:
        try:
            # Mengambil data harian dari Sectors.app
            url = f"https://sectors.app/api/stock/daily/{ticker}/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                raw_data = response.json()
                
                # Sectors.app biasanya mengembalikan list objek harian
                # Kita ambil data paling terakhir (indeks -1)
                if isinstance(raw_data, list) and len(raw_data) > 0:
                    latest = raw_data[-1]
                elif isinstance(raw_data, dict) and 'data' in raw_data:
                    latest = raw_data['data'][-1]
                else:
                    continue

                last_price = float(latest.get('close', 0))
                prev_price = float(latest.get('prev_close', 0))
                
                # Hitung Perubahan
                if prev_price > 0:
                    change = ((last_price - prev_price) / prev_price) * 100
                else:
                    change = 0
                
                # Logika PREDATOR Core v16.4
                if change > 1.5:
                    signal = "STRONG BUY"
                elif change > 0:
                    signal = "BUY"
                elif change < -1.5:
                    signal = "STRONG SELL"
                elif change < 0:
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
            print(f"Error fetching {ticker}: {e}")
            continue
            
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    data = get_sectors_signals()
    # Jika data kosong karena API limit, kirim status standby
    if not data:
        return jsonify([{"ticker": "API", "price": "LIMIT", "change": 0, "signal": "RETRYING"}]), 200
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
