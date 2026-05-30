from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import FinanceDataReader as fdr
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scan")
def scan_market():

    result = []

    # 코스피200 + 코스닥150
    kospi = fdr.StockListing("KOSPI").head(200)
    kosdaq = fdr.StockListing("KOSDAQ").head(150)

    stocks = list(kospi.iterrows()) + list(kosdaq.iterrows())

    for _, stock in stocks:

        try:

            code = stock["Code"]
            name = stock["Name"]

            df = fdr.DataReader(code)

            if len(df) < 120:
                continue

            volumes = df["Volume"].astype(np.int64)

            recent = volumes.tail(60)

            recent_max = int(recent.max())
            all_time_max = int(volumes.max())

            recent_idx = recent.idxmax()
            all_time_idx = volumes.idxmax()

            recent_days_ago = (
                df.index[-1] - recent_idx
            ).days

            all_time_months_ago = round(
                (df.index[-1] - all_time_idx).days / 30,
                1
            )

            recent_close = int(
                df.loc[recent_idx]["Close"]
            )

            current_close = int(
                df["Close"].iloc[-1]
            )

            latest_volume = int(
                df["Volume"].iloc[-1]
            )

            trade_value = (
                current_close * latest_volume
            )

            # 거래대금 필터
            if trade_value < 10000000000:
                continue

            volume_ratio = round(
                (recent_max / all_time_max) * 100,
                2
            )

            result.append({
                "code": code,
                "name": name,
                "recentMax": recent_max,
                "volumeRatio": volume_ratio,
                "recentDaysAgo": recent_days_ago,
                "recentClose": f"{recent_close:,}",
                "currentClose": f"{current_close:,}",
                "allTimeMonthsAgo": all_time_months_ago
            })

        except:
            continue

    result = sorted(
        result,
        key=lambda x: -x["volumeRatio"]
    )

    return result[:10]
