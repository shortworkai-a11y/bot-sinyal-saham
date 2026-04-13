from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

WATCHLIST = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO', 'ADRO', 'BBNI']

def get_data_from_yahoo(ticker):
    """Fungsi Cadangan jika Sectors.app gagal"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.JK?interval=1d&range=2d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()['chart']['result'][0]
        last_price = data['indicators']['quote'][0]['close'][-1]
        prev_close = data['meta']['previousClose']
        change = ((last_price - prev_close) / prev_close) * 100
        return last_price, change
    except:
        return None, None

def get_market_data():
    data_list = []
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}

    for ticker in WATCHLIST:
        last_price, change = None, None
        
        # COBA SUMBER 1: Sectors.app
        try:
            url = f"https://sectors.app/api/stock/daily/{ticker}/"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                raw = res.json()
                latest = raw[-1] if isinstance(raw, list) else raw['data'][-1]
                last_price = float(latest.get('close', 0))
                prev = float(latest.get('prev_close', 0))
                change = ((last_price - prev) / prev) * 100 if prev > 0 else 0
        except:
            pass

        # COBA SUMBER 2: Yahoo Finance (Jika Sectors Gagal)
        if last_price is None:
            last_price, change = get_data_from_yahoo(ticker)

        # JIKA BERHASIL DAPAT DATA (DARI MANAPUN)
        if last_price is not None:
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
            
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    return jsonify(get_market_data())

if __name__ == '__main__':
    app.run()
