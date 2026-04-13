from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Daftar saham (Menggunakan .JK untuk Bursa Efek Indonesia)
WATCHLIST = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK', 'ADRO.JK', 'BBNI.JK']

def get_yahoo_data():
    data_list = []
    # Header browser agar tidak diblokir Yahoo
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for ticker in WATCHLIST:
        try:
            # Menggunakan API v8 Yahoo yang sangat cepat
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                json_data = response.json()
                result = json_data['chart']['result'][0]
                
                # Mengambil harga penutupan terbaru
                prices = result['indicators']['quote'][0]['close']
                # Cari harga terakhir yang tidak bernilai None
                valid_prices = [p for p in prices if p is not None]
                
                if valid_prices:
                    last_price = valid_prices[-1]
                    prev_close = result['meta']['previousClose']
                    
                    # Hitung Perubahan Persentase
                    change = ((last_price - prev_close) / prev_close) * 100
                    
                    # Logika Sinyal Predator
                    if change > 1.5: signal = "STRONG BUY"
                    elif change > 0: signal = "BUY"
                    elif change < -1.5: signal = "STRONG SELL"
                    elif change < 0: signal = "SELL"
                    else: signal = "NEUTRAL"

                    data_list.append({
                        'ticker': ticker.replace('.JK', ''),
                        'price': f"{last_price:,.0f}",
                        'change': round(change, 2),
                        'signal': signal
                    })
        except Exception as e:
            print(f"Gagal mengambil {ticker}: {e}")
            continue
            
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    data = get_yahoo_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run()
