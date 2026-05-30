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

# 코스피 시총 상위 30개 테스트용
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
    ("035720","카카오"),
    ("051910","LG화학"),
    ("006400","삼성SDI"),
    ("028260","삼성물산"),
    ("032830","삼성생명"),
    ("017670","SK텔레콤"),
    ("086790","하나금융지주"),
    ("003670","포스코홀딩스"),
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
    ("030200","KT")
]

@app.get("/scan")
def scan_market():

    result = []

    for code, name in TOP30_CODES:

        try:

            # 속도 개선
            df = fdr.DataReader(
                code,
                "2020-01-01"
            )

            if len(df) < 60:
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

            profit_rate = round(
                ((current_close - recent_close)
                 / recent_close) * 100,
                2
            )

            # 역대 거래량 순위
            volume_rank = int(
                (volumes > recent_max).sum()
            ) + 1

            volume_ratio = round(
                (recent_max / all_time_max) * 100,
                2
            )

            result.append({

                "code": code,
                "name": name,

                "recentMax":
                    f"{recent_max:,}",

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

                "allTimeMonthsAgo":
                    all_time_months_ago,

                "volumeRank":
                    volume_rank,

                "volumeRatio":
                    volume_ratio

            })

        except Exception as e:
            print(code, e)

    result = sorted(
        result,
        key=lambda x: (
            x["volumeRank"],
            -x["volumeRatio"]
        )
    )

    return result
