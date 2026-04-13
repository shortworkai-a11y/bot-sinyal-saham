from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_indonesia_market_data():
    # Mengambil data fundamental lengkap dari public source sectors.app
    url = "https://sectors.app/api/stock/report/" 
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def apply_sovereign_filters(stocks):
    results = {'small': [], 'mid': [], 'big': []}
    
    for s in stocks:
        try:
            price = float(s.get('last_price', 0))
            if price <= 0: continue

            # Ambil data indikator
            pe = float(s.get('pe_ttm', 999))
            pbv = float(s.get('pbv', 999))
            roe = float(s.get('roe', 0))
            growth = float(s.get('net_income_growth_yoy', 0))
            der = float(s.get('der', 999))
            ocf = float(s.get('operating_cashflow', 0))

            # Hitung Skor Kriteria (Total 7)
            score = 0
            if pe < 12: score += 1
            if pbv < 1.5: score += 1
            if roe > 12: score += 1
            if growth > 0: score += 1
            if der < 1: score += 1
            if ocf > 0: score += 1
            score += 1 # Poin dasar untuk validitas harga

            # Ambil yang skornya minimal 4/7 agar dashboard terisi
            if score >= 4:
                status = "PREMIUM" if score == 7 else "POTENTIAL"
                
                stock_data = {
                    'symbol': s.get('symbol', 'N/A'),
                    'price': price,
                    'pe': round(pe, 2) if pe < 900 else "N/A",
                    'pbv': round(pbv, 2) if pbv < 900 else "N/A",
                    'roe': round(roe, 2),
                    'der': round(der, 2),
                    'score': score,
                    'status': status
                }

                if price < 300:
                    results['small'].append(stock_data)
                elif price < 2000:
                    results['mid'].append(stock_data)
                else:
                    results['big'].append(stock_data)
        except:
            continue
            
    # Sortir berdasarkan skor tertinggi
    for key in results:
        results[key] = sorted(results[key], key=lambda x: x['score'], reverse=True)
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
