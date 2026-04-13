from flask import Flask, render_template, jsonify
import requests
import yfinance as yf

app = Flask(__name__)

# List Top Saham IDX sebagai cadangan jika API utama gagal
BACKUP_TICKERS = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK', 'ADRO.JK', 'UNVR.JK', 'ICBP.JK', 'PTBA.JK']

def get_data_from_sectors():
    try:
        url = "https://sectors.app/api/stock/report/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def get_data_from_yahoo():
    """Fungsi Cadangan: Mengambil data dasar jika Sectors API mati"""
    data_list = []
    try:
        tickers = yf.download(BACKUP_TICKERS, period="1d", group_by='ticker', progress=False)
        for t in BACKUP_TICKERS:
            try:
                info = yf.Ticker(t).info
                data_list.append({
                    'symbol': t.replace('.JK', ''),
                    'company_name': info.get('longName', 'N/A'),
                    'last_price': info.get('currentPrice', 0),
                    'pe_ttm': info.get('trailingPE', 0),
                    'pbv': info.get('priceToBook', 0),
                    'roe': (info.get('returnOnEquity', 0) * 100),
                    'net_income_growth_yoy': (info.get('revenueGrowth', 0) * 100),
                    'der': info.get('debtToEquity', 0),
                    'operating_cashflow': info.get('operatingCashflow', 1) # Default 1 agar lolos filter
                })
            except: continue
    except: pass
    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    # Coba sumber utama
    stocks = get_data_from_sectors()
    
    # Jika kosong, gunakan cadangan Yahoo
    if not stocks:
        stocks = get_data_from_yahoo()

    results = {'small': [], 'mid': [], 'big': []}
    
    for s in stocks:
        try:
            price = float(s.get('last_price', 0))
            if price <= 0: continue

            pe = float(s.get('pe_ttm', 0))
            pbv = float(s.get('pbv', 0))
            roe = float(s.get('roe', 0))
            growth = float(s.get('net_income_growth_yoy', 0))
            der = float(s.get('der', 0))
            ocf = float(s.get('operating_cashflow', 0))

            # Hitung Skor (Kriteria Anda)
            score = 0
            if 0 < pe < 12: score += 1
            if 0 < pbv < 1.5: score += 1
            if roe > 12: score += 1
            if growth > 0: score += 1
            if der < 1 and der != 0: score += 1
            if ocf > 0: score += 1

            stock_data = {
                'symbol': s.get('symbol', 'N/A'),
                'name': s.get('company_name', 'N/A'),
                'price': price,
                'pe': round(pe, 2) if pe != 0 else "N/A",
                'pbv': round(pbv, 2) if pbv != 0 else "N/A",
                'roe': round(roe, 2),
                'der': round(der, 2),
                'score': score,
                'status': "PREMIUM" if score >= 5 else ("POTENTIAL" if score >= 3 else "REGULAR")
            }

            if price < 300: results['small'].append(stock_data)
            elif price < 2000: results['mid'].append(stock_data)
            else: results['big'].append(stock_data)
        except: continue
            
    for key in results:
        results[key] = sorted(results[key], key=lambda x: x['score'], reverse=True)
    return jsonify(results)

if __name__ == '__main__':
    app.run()
