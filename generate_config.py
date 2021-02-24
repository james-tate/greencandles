import pandas as pd

# coin : the coin
# currentcap : current capital the bot is allowed to spend on a purchase of this coin
# starting : price of the coin when purchased
# limit : if purchased, if price falls below this sell 
# currentPrice : the current price during the polling interval
# autobought : how many shares the bot has purchased, this is needed incase we manually buy some
# updatetime : the polling interval for this coin

coinCaps = [
['ADAUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ALGOUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ATOMUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['BANDUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['BATUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['BCHUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['BNBUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['BTCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['DASHUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['DOGEUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['EGLDUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ENJUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['EOSUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ETCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ETHUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['HBARUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['HNTUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ICXUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['IOTAUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['KNCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['LINKUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['LTCUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['MANAUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['MATICUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['NANOUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['NEOUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['OMGUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ONEUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ONTUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['OXTUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['QTUMUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['REPUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['RVNUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['SOLUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['STORJUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['UNIUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['VETUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['WAVESUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['XLMUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['XTZUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ZECUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ZENUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ZILUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0],
['ZRXUSD', 12.0, 0.0, 0.0, 0.0, 0.0, .999, 180, "none", 0.0, "none", 0]
]
# for x in coinCaps:
# 	df.append(coinCaps)
df = pd.DataFrame(coinCaps, columns = ['coin', 'capital', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime', 'orderid', 'takeProfitAmount', 'takeProfitOrder', 'delta'])
df.set_index('coin', inplace=True)
df.to_csv(f'config.csv', mode='w', header=False, index=True)
	