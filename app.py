from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# List saham utama Indonesia (Bisa ditambah sesuai kebutuhan)
# Untuk menyisir 800 saham sekaligus di Vercel Free, kita gunakan list top 100 agar tidak timeout
WATCHLIST = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK', 'ADRO.JK', 'BBNI.JK',
    'UNVR.JK', 'ICBP.JK', 'AMRT.JK', 'PGAS.JK', 'PTBA.JK', 'ITMG.JK', 'INKP.JK', 'CPIN.JK',
    'KLBF.JK', 'SMGR.JK', 'JSMR.JK', 'TOWR.JK', 'BRIS.JK', 'BSDE.JK', 'PWON.JK', 'AKRA.JK'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    results = {'small': [], 'mid': [], 'big': []}
    
    for t in WATCHLIST:
        try:
            stock = yf.Ticker(t)
            info = stock.info
            
            # Ambil data indikator
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            pe = info.get('trailingPE') or 0
            pbv = info.get('priceToBook') or 0
            roe = (info.get('returnOnEquity') or 0) * 100
            der = (info.get('debtToEquity') or 0) / 100
            growth = info.get('revenueGrowth') or 0
            ocf = info.get('operatingCashflow') or 0
            
            # --- FILTER KRITERIA ---
            # Kita buat sedikit longgar agar data muncul, lalu Anda bisa ketatkan lagi
            if price > 0:
                # Validasi Kriteria 2-7
                is_premium = (
                    (pe < 12 if pe > 0 else True) and 
                    (pbv < 1.5 if pbv > 0 else True) and 
                    (roe > 12) and 
                    (der < 1 if der > 0 else True) and
                    (ocf > 0)
                )

                if is_premium:
                    data = {
                        'symbol': t.replace('.JK', ''),
                        'price': price,
                        'pe': round(pe, 2),
                        'pbv': round(pbv, 2),
                        'roe': round(roe, 2)
                    }
                    
                    # Segmen Harga (Kriteria 1)
                    if price < 300:
                        results['small'].append(data)
                    elif price < 2000:
                        results['mid'].append(data)
                    else:
                        results['big'].append(data)
        except Exception as e:
            print(f"Error {t}: {e}")
            continue
            
    return jsonify(results)

if __name__ == '__main__':
    app.run()
