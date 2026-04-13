from flask import Flask, render_template, jsonify
import yfinance as yf

app = Flask(__name__)

# Batasi watchlist menjadi 5 saham paling likuid agar fetch sangat cepat
WATCHLIST = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    data_list = []
    try:
        # Gunakan string tunggal untuk download agar lebih efisien
        tickers_string = " ".join(WATCHLIST)
        # Ambil data period 2 hari saja (hari ini dan kemarin)
        data = yf.download(tickers_string, period="2d", interval="1d", group_by='ticker', progress=False)
        
        for t in WATCHLIST:
            try:
                # Ambil dataframe untuk masing-masing ticker
                df = data[t]
                if len(df) >= 2:
                    last_price = float(df['Close'].iloc[-1])
                    prev_close = float(df['Close'].iloc[-2])
                    change = ((last_price - prev_close) / prev_close) * 100
                    
                    # Logika Sinyal Sederhana
                    signal = "BUY" if change > 0 else "SELL"
                    if abs(change) < 0.1: signal = "NEUTRAL"
                    if change > 1.5: signal = "STRONG BUY"
                    if change < -1.5: signal = "STRONG SELL"

                    data_list.append({
                        'ticker': t.replace('.JK', ''),
                        'price': f"{last_price:,.0f}",
                        'change': round(change, 2),
                        'signal': signal
                    })
            except:
                continue
    except Exception as e:
        print(f"Error: {e}")
        
    return jsonify(data_list)

if __name__ == '__main__':
    app.run()
