from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import FinanceDataReader as fdr
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/scan')
def scan_market():

    result = []

    stocks = fdr.StockListing('KRX')

    # 속도 최적화
    stocks = stocks.head(100)

    for _, stock in stocks.iterrows():

        try:

            code = stock['Code']
            name = stock['Name']

            df = fdr.DataReader(code)

            if len(df) < 120:
                continue

            volumes = df['Volume'].astype(np.int64)

            recent_3m_max = int(volumes.tail(60).max())
            all_time_max = int(volumes.max())

            latest_volume = int(volumes.iloc[-1])

            volume_ratio = round(
                (recent_3m_max / all_time_max) * 100,
                2
            )

            latest_close = int(df['Close'].iloc[-1])
            prev_close = int(df['Close'].iloc[-2])

            change_rate = round(
                ((latest_close - prev_close) / prev_close) * 100,
                2
            )

            trade_value = latest_close * latest_volume

            if trade_value < 10000000000:
                continue

            result.append({
                'code': code,
                'name': name,
                'recentMax': recent_3m_max,
                'allTimeMax': all_time_max,
                'price': f'{latest_close:,}',
                'change': f'{change_rate:+.2f}%',
                'value': f'{round(trade_value / 100000000,1)}억',
                'volumeRatio': volume_ratio
            })

        except:
            continue

    result = sorted(
        result,
        key=lambda x: (
            -x['volumeRatio'],
            -float(x['value'].replace('억',''))
        )
    )

    return result[:50]
