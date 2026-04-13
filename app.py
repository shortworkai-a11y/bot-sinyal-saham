def apply_sovereign_filters(stocks):
    results = {'small': [], 'mid': [], 'big': []}
    
    for s in stocks:
        try:
            price = float(s.get('last_price', 0))
            if price == 0: continue

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
            # (Tambahan 1 poin jika harganya valid)
            score += 1

            # Tampilkan saham yang skornya minimal 5 dari 7 (Hampir Premium)
            if score >= 5:
                status = "PREMIUM" if score == 7 else "POTENTIAL"
                
                stock_data = {
                    'symbol': s.get('symbol'),
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
            
    # Urutkan berdasarkan skor tertinggi
    for cat in results:
        results[cat] = sorted(results[cat], key=lambda x: x['score'], reverse=True)
        
    return results
