import greenCandles as candles

'''
{
	'symbol': 'BTCUSDC', 
	'bidPrice': '57905.70000000', 
	'bidQty': '0.01136100', 
	'askPrice': '57917.82000000', 
	'askQty': '0.00456500'
	}
'''

coin = "ETHUSD"
connector = candles.BinaceConnector()
tickers = connector.getBook()
for x in tickers:
	print(x)
	# if coin == x['symbol']:
	# 	print(x['symbol'], end="\t\t")
	# 	print(x['bidPrice'])