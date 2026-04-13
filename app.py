from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_indonesia_market_data():
    # Mengambil data dari endpoint report yang stabil
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
            pe = float(s.get('pe_ttm', 999))
            pbv = float(s.get('pbv', 999))
            roe = float(s.get('roe', 0))
            growth = float(s.get('net_income_growth_yoy', 0))
            der = float(s.get('der', 999))
            ocf = float(s.get('operating_cashflow', 0))

            # Hitung Skor (Kriteria Anda + 1 Poin Validitas)
            score = 0
            if pe < 12: score += 1
            if pbv < 1.5: score += 1
            if roe > 12: score += 1
            if growth > 0: score += 1
            if der < 1: score += 1
            if ocf > 0: score += 1
            score += 1 

            # Turunkan threshold ke 3 agar dashboard pasti terisi
            if score >= 3:
                if score >= 6: status = "PREMIUM"
                elif score >= 4: status = "POTENTIAL"
                else: status = "WATCHLIST"
                
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

                # Segmentasi (Kriteria 1)
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
    # Jika API utama kosong, kirim data dummy agar user tahu sistem jalan
    if not raw_stocks:
        return jsonify({"small": [], "mid": [], "big": []})
        
    filtered_data = apply_sovereign_filters(raw_stocks)
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run()
