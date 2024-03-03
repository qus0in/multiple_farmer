# Multiple Farmer
> `토스 모으기`로 `레버리지 ETF` `시스템 트레이딩` <br>
> `농부`지만 마음이 많이 급한...

![농부](./multiple_farmer.png)

## Idea
* 2일부터 232일까지의 피보나치 수열 수익률을 기간 가중(짧을수록 가중)으로 평균하여 스코어링
* 스코어가 25위 안에 든 종목에 한해서 매수 시작. 이탈 시 즉시 매도
* 20일 동안 10$씩 매수하고, 총 평가액이 200$ 도달 시 매도
* 50$ 매수 후, 232일의 AATR의 2.58배(99% 표준분포) 이상 수익 시 익절

## Install
```shell
$ python3 -m venv venv # or python -m venv venv
$ source venv/bin/activate # or source venv/scripts/activate
$ pip install -r requirements.txt
$ python -m streamlit run app.py
```