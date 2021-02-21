import pandas as pd

# coin : the coin
# currentcap : current capital the bot is allowed to spend on a purchase of this coin
# starting : price of the coin when purchased
# limit : if purchased, if price falls below this sell 
# currentPrice : the current price during the polling interval
# autobought : how many shares the bot has purchased, this is needed incase we manually buy some
# updatetime : the polling interval for this coin

coinCaps = [
['ADAUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ALGOUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ATOMUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BANDUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BATUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BCHUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BNBUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['BTCUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['DASHUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['DOGEUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['EGLDUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ENJUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['EOSUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ETCUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ETHUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['HBARUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['HNTUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ICXUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['IOTAUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['KNCUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['LINKUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['LTCUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['MANAUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['MATICUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['NANOUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['NEOUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['OMGUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ONEUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ONTUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['OXTUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['QTUMUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['REPUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['RVNUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['SOLUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['STORJUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['UNIUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['VETUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['WAVESUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['XLMUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['XTZUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZECUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZENUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZILUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180],
['ZRXUSD',15, 0.0, 0.0, 0.0, 0.0, .99, 180]
]

# for x in coinCaps:
# 	df.append(coinCaps)
df = pd.DataFrame(coinCaps, columns = ['coin', 'currentcap', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime'])
df.set_index('coin', inplace=True)
df.to_csv(f'config.csv', mode='w', header=False, index=True)
	