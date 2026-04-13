from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_indonesia_market_data():
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

            # Ambil data indikator finansial
            pe = float(s.get('pe_ttm', 0))
            pbv = float(s.get('pbv', 0))
            roe = float(s.get('roe', 0))
            growth = float(s.get('net_income_growth_yoy', 0))
            der = float(s.get('der', 0))
            ocf = float(s.get('operating_cashflow', 0))

            # Hitung Skor Kriteria (Total 6 Indikator Utama)
            score = 0
            if 0 < pe < 12: score += 1
            if 0 < pbv < 1.5: score += 1
            if roe > 12: score += 1
            if growth > 0: score += 1
            if der < 1: score += 1
            if ocf > 0: score += 1

            # Tentukan Status Label
            if score >= 5: status = "PREMIUM"
            elif score >= 3: status = "POTENTIAL"
            else: status = "REGULAR"
            
            stock_data = {
                'symbol': s.get('symbol', 'N/A'),
                'name': s.get('company_name', ''),
                'price': price,
                'pe': round(pe, 2) if pe != 0 else "N/A",
                'pbv': round(pbv, 2) if pbv != 0 else "N/A",
                'roe': round(roe, 2),
                'der': round(der, 2),
                'score': score,
                'status': status
            }

            # Masukkan ke segmen (TIDAK ADA FILTER LAGI, SEMUA MASUK)
            if price < 300:
                results['small'].append(stock_data)
            elif price < 2000:
                results['mid'].append(stock_data)
            else:
                results['big'].append(stock_data)
        except:
            continue
            
    # Urutkan berdasarkan skor tertinggi agar yang terbaik tetap di atas
    for key in results:
        results[key] = sorted(results[key], key=lambda x: x['score'], reverse=True)
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    raw_stocks = get_indonesia_market_data()
    if not raw_stocks:
        return jsonify({"small": [], "mid": [], "big": []})
    filtered_data = apply_sovereign_filters(raw_stocks)
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run()
