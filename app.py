from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Gunakan API Key jika ada, jika tidak, biarkan kosong untuk publik
SECTORS_API_KEY = "" 

def fetch_all_indonesia_stocks():
    """Mengambil data fundamental lengkap seluruh emiten di Indonesia"""
    url = "https://sectors.app/api/stock/report/" # Endpoint laporan lengkap
    headers = {'Authorization': SECTORS_API_KEY} if SECTORS_API_KEY else {}
    
    try:
        # Note: Pengambilan data massal mungkin butuh optimasi atau caching
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return []
        return response.json()
    except:
        return []

def filter_logic(stocks):
    results = {'small': [], 'mid': [], 'big': []}
    
    for s in stocks:
        try:
            # 1. Ambil Data Dasar
            price = float(s.get('last_price', 0))
            pe = float(s.get('pe_ttm', 100))
            pbv = float(s.get('pbv', 100))
            roe = float(s.get('roe', 0))
            ni_growth = float(s.get('net_income_growth_yoy', -1))
            der = float(s.get('der', 100))
            ocf = float(s.get('operating_cashflow', -1))

            # 2. Filter Sesuai Request (Kriteria 2-7)
            if (pe < 12 and pbv < 1.5 and roe > 12 and 
                ni_growth > 0 and der < 1 and ocf > 0):
                
                stock_data = {
                    'symbol': s.get('symbol'),
                    'name': s.get('company_name', ''),
                    'price': price,
                    'pe': pe,
                    'pbv': pbv,
                    'roe': roe
                }

                # 3. Pengelompokan Segmen (Kriteria 1)
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
    all_stocks = fetch_all_indonesia_stocks()
    filtered = filter_logic(all_stocks)
    return jsonify(filtered)

if __name__ == '__main__':
    app.run()
