import pandas as pd

# coin : the coin
# currentcap : current capital the bot is allowed to spend on a purchase of this coin
# starting : price of the coin when purchased
# limit : if purchased, if price falls below this sell 
# currentPrice : the current price during the polling interval
# autobought : how many shares the bot has purchased, this is needed incase we manually buy some
# updatetime : the polling interval for this coin

coinCaps = [
['ADAUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ALGOUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ATOMUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BANDUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BATUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BCHUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BNBUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BTCUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['DASHUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['DOGEUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['EGLDUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ENJUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['EOSUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ETCUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ETHUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['HBARUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['HNTUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ICXUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['IOTAUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['KNCUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['LINKUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['LTCUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['MANAUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['MATICUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['NANOUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['NEOUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['OMGUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ONEUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ONTUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['OXTUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['QTUMUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['REPUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['RVNUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['SOLUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['STORJUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['UNIUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['VETUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['WAVESUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['XLMUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['XTZUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZECUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZENUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZILUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZRXUSD',20, 0.0, 0.0, 0.0, 0.0, .99, 180]
]

# for x in coinCaps:
# 	df.append(coinCaps)
df = pd.DataFrame(coinCaps, columns = ['coin', 'currentcap', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime'])
df.set_index('coin', inplace=True)
df.to_csv(f'config.csv', mode='w', header=False, index=True)
	