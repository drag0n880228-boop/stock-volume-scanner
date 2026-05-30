from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import FinanceDataReader as fdr
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOP30_CODES = [
    ("005930","삼성전자"),
    ("000660","SK하이닉스"),
    ("373220","LG에너지솔루션"),
    ("207940","삼성바이오로직스"),
    ("005380","현대차"),
    ("012330","현대모비스"),
    ("068270","셀트리온"),
    ("035420","NAVER"),
    ("105560","KB금융"),
    ("055550","신한지주"),
    ("051910","LG화학"),
    ("006400","삼성SDI"),
    ("028260","삼성물산"),
    ("032830","삼성생명"),
    ("017670","SK텔레콤"),
    ("086790","하나금융지주"),
    ("003670","POSCO홀딩스"),
    ("066570","LG전자"),
    ("015760","한국전력"),
    ("034730","SK"),
    ("018260","삼성에스디에스"),
    ("000270","기아"),
    ("010130","고려아연"),
    ("009540","HD한국조선해양"),
    ("033780","KT&G"),
    ("316140","우리금융지주"),
    ("024110","기업은행"),
    ("267250","HD현대"),
    ("030200","KT"),
    ("035720","카카오")
]

@app.get("/scan")
def scan_market():

    result = []

    for code, name in TOP30_CODES:

        try:

            df = fdr.DataReader(
                code,
                "2020-01-01"
            )

            if len(df) < 100:
                continue

            volumes = df["Volume"].astype(np.int64)

            recent_df = df.tail(60)

            recent_max_idx = recent_df["Volume"].idxmax()

            recent_max_volume = int(
                recent_df.loc[recent_max_idx]["Volume"]
            )

            recent_close = int(
                recent_df.loc[recent_max_idx]["Close"]
            )

            current_close = int(
                df["Close"].iloc[-1]
            )

            profit_rate = round(
                (
                    (current_close - recent_close)
                    / recent_close
                ) * 100,
                2
            )

            all_time_max_idx = volumes.idxmax()

            all_time_max = int(
                volumes.max()
            )

            volume_ratio = round(
                recent_max_volume
                / all_time_max
                * 100,
                2
            )

            sorted_volumes = (
                volumes
                .sort_values(ascending=False)
                .reset_index(drop=True)
            )

            volume_rank = (
                sorted_volumes[
                    sorted_volumes
                    > recent_max_volume
                ].count()
                + 1
            )

            recent_days_ago = (
                df.index[-1]
                - recent_max_idx
            ).days

            all_time_months_ago = round(
                (
                    df.index[-1]
                    - all_time_max_idx
                ).days / 30,
                1
            )

            result.append({

                "code": code,
                "name": name,

                "volumeRatio": volume_ratio,

                "volumeRank": int(
                    volume_rank
                ),

                "recentMax":
                    f"{recent_max_volume:,}",

                "recentDate":
                    recent_max_idx.strftime(
                        "%Y-%m-%d"
                    ),

                "recentDaysAgo":
                    recent_days_ago,

                "recentClose":
                    f"{recent_close:,}",

                "currentClose":
                    f"{current_close:,}",

                "profitRate":
                    profit_rate,

                "allTimeMax":
                    f"{all_time_max:,}",

                "allTimeDate":
                    all_time_max_idx.strftime(
                        "%Y-%m-%d"
                    ),

                "allTimeMonthsAgo":
                    all_time_months_ago

            })

        except Exception as e:
            print(code, e)

    result = sorted(
        result,
        key=lambda x: (
            -x["volumeRatio"],
            x["volumeRank"]
        )
    )

    return result[:10]
