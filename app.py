from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_indonesia_market_data():
    # Mengambil data fundamental lengkap dari public source sectors.app
    # API ini jauh lebih cepat daripada yfinance untuk scanning massal
    url = "https://sectors.app/api/stock/report/" 
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def apply_sovereign_filters(stocks):
    results = {'small': [], 'mid': [], 'big': []}
    
    for s in stocks:
        try:
            # Mengambil data indikator dari JSON
            price = float(s.get('last_price', 0))
            # Kriteria 2-7
            pe = float(s.get('pe_ttm', 999))
            pbv = float(s.get('pbv', 999))
            roe = float(s.get('roe', 0))
            growth = float(s.get('net_income_growth_yoy', 0))
            der = float(s.get('der', 999))
            ocf = float(s.get('operating_cashflow', 0))

            # LOGIKA FILTER KETAT
            if (pe < 12 and pbv < 1.5 and roe > 12 and 
                growth > 0 and der < 1 and ocf > 0):
                
                stock_data = {
                    'symbol': s.get('symbol'),
                    'name': s.get('company_name', ''),
                    'price': price,
                    'pe': round(pe, 2),
                    'pbv': round(pbv, 2),
                    'roe': round(roe, 2),
                    'der': round(der, 2)
                }

                # 1. SEGMENTASI HARGA (Kriteria 1)
                if price < 300:
                    results['small'].append(stock_data)
                elif price < 2000:
                    results['mid'].append(stock_data)
                else:
                    results['big'].append(stock_data)
        except:
            continue
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    raw_stocks = get_indonesia_market_data()
    filtered_data = apply_sovereign_filters(raw_stocks)
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run()
