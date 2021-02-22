import pandas as pd

# coin : the coin
# currentcap : current capital the bot is allowed to spend on a purchase of this coin
# starting : price of the coin when purchased
# limit : if purchased, if price falls below this sell 
# currentPrice : the current price during the polling interval
# autobought : how many shares the bot has purchased, this is needed incase we manually buy some
# updatetime : the polling interval for this coin

coinCaps = [
['ADAUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ALGOUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ATOMUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['BANDUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['BATUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['BCHUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['BNBUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['BTCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['DASHUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['DOGEUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['EGLDUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ENJUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['EOSUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ETCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ETHUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['HBARUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['HNTUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ICXUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['IOTAUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['KNCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['LINKUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['LTCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['MANAUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['MATICUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['NANOUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['NEOUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['OMGUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ONEUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ONTUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['OXTUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['QTUMUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['REPUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['RVNUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['SOLUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['STORJUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['UNIUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['VETUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['WAVESUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['XLMUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['XTZUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ZECUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ZENUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ZILUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180],
['ZRXUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180]
]

# for x in coinCaps:
# 	df.append(coinCaps)
df = pd.DataFrame(coinCaps, columns = ['coin', 'currentcap', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime'])
df.set_index('coin', inplace=True)
df.to_csv(f'config.csv', mode='w', header=False, index=True)
	