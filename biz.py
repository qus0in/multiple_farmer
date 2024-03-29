import time
from streamlit import cache_data
import requests
import yfinance as yf
import pandas as pd

@cache_data
def get_periods():
    periods = [0] * 13
    periods[0], periods[1] = 1, 1
    for i in range(2, len(periods)):
        periods[i] = periods[i-1] + periods[i-2]
    return periods[2:]

periods = get_periods()
exclusion = ['FNGO', 'SPUU', 'FBGX', 'TECS']

class Screener:
    @classmethod
    @cache_data(ttl=3600, show_spinner=True)
    def get_history(cls, ticker: str) -> pd.DataFrame:
        return yf.Ticker(ticker).history(period='1y')
    
    @classmethod
    @cache_data(ttl=3600, show_spinner=True)
    def get_score(cls, ticker: str, shift=0) -> float:
        c: pd.Series = cls.get_history(ticker).Close.shift(shift)
        def score_from_period(period):
            return c.rolling(period).apply(
                lambda x: (x.iloc[-1] / x.iloc[0] - 1) / period).iloc[-1]
        sum_val = sum([score_from_period(p)
                       for p in periods])
        return sum_val / len(periods) * 252

    @classmethod
    @cache_data(ttl=3600, show_spinner=True)
    def get_target_yield(cls, ticker) -> float:
        history = cls.get_history(ticker)
        concat = lambda *x: pd.concat(x, axis=1)
        th = concat(history.High, history.Close.shift(1)).max(axis=1)
        tl = concat(history.Low, history.Close.shift(1)).min(axis=1)
        atr = (th - tl).ewm(span=max(periods)).mean()
        aatr = atr.iloc[-1] / history.Close.iloc[-1]
        return max(5, min(10, int(aatr * 2.58 * 100)))
    
    @classmethod
    @cache_data(ttl=3600, show_spinner=True)
    def fetch_etf_list(cls) -> pd.DataFrame:
        URL = 'https://etfdb.com/api/screener/'
        objs = []
        payload = lambda page: dict(
                asset_class="equity",
                leveraged=['-3x','-2x','2x','3x'],
                active_or_passive="Passive",
                only=['data'], page=page)
        handle_row = lambda row: dict(symbol=row['symbol']['text'],
                name=row['name']['text'],         
                assets=int(row['assets'].replace('$','').replace(',', '')),
                volume=int(row['average_volume'].replace(',', '')))
        for page in range(1, 5):
            while 1:
                try: response = requests.post(URL, json=payload(page)); break
                except requests.exceptions.ConnectionError:
                    print('Connection Error'); time.sleep(5)
            response.raise_for_status()
            data = [handle_row(row) for row in response.json()['data']]
            objs.append(pd.DataFrame(data))
        return pd.concat(objs)
    
    @classmethod
    @cache_data(ttl=3600, show_spinner=True)
    def get_table(cls):
        df = cls.fetch_etf_list()
        q = 'assets > assets.max() ** 0.5 or volume > volume.mean()'
        df.query(q, inplace=True)
        q2 = f'not symbol.str.contains("{"|".join(exclusion)}")'
        df.query(q2, inplace=True)
        df['score'] = [cls.get_score(t) for t in df.symbol]
        df['score_yst'] = [cls.get_score(t, shift=1) for t in df.symbol]
        df['target_yield'] = [cls.get_target_yield(t) for t in df.symbol]
        df.sort_values(by='score', ascending=False, inplace=True)
        table = df.set_index('symbol')

        td = table.head(25)
        ys = table.sort_values(by='score_yst', ascending=False).head(25)
        mg = td.merge(ys, how='outer', on='symbol', indicator=True)

        def get_diff(query, col):
            return mg.query(query).loc[:, [col]].rename(columns={col: 'name'})

        t1 = get_diff('_merge == "left_only"', 'name_x')
        t2 = get_diff('_merge == "right_only"', 'name_y')

        return td, t1, t2