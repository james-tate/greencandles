#!/usr/bin/python3

# some code from this repo has been inspired from https://github.com/hackingthemarket
# https://www.youtube.com/channel/UCY2ifv8iH1Dsgjrz-h3lWLQ

from binance.client import Client
from binance.enums import *
import time
from binance.websockets import BinanceSocketManager
from binance.depthcache import DepthCacheManager
import pandas as pd
import sys
sys.path.append('../')
import clientConfig

from filelock import Timeout, FileLock

#this will handle the connection to binace
class BinaceConnector():
	def __init__(self):
		self.client = Client(clientConfig.api_key, clientConfig.api_secret, tld='us')
		self.wsclient = None

	# setup a websocket client
	def setupWebsocket(self):
		self.wsclient = BinanceSocketManager(self.client)
		return self.wsclient

	# get a feed in real time for all prices
	def startAllBookTicker(self, callback):
		return self.client.start_book_ticker_socket(callback)

	# setup depth manager
	def setupDepthCacheManager(self, coin, callback, limit=10):
		return DepthCacheManager(self.client, coin, callback)

	def setupCandleSocket(self, coin, callback, interval):
		self.setupWebsocket()
		return self.wsclient.start_kline_socket(coin, callback, interval=interval)

	def setupSocketMultiPlex(self, coins, multimessage):
		self.wsclient.start_multiplex_socket(coins, multimessage)
		return self.wsclient

	def getHistoryCandles(self, coin, interval=Client.KLINE_INTERVAL_5MINUTE, len='100 hour ago EST'):
		return self.client.get_historical_klines(coin, interval, len)

	# setup multiple cache managers:
	def setupDepthForSymbolsUSDT(self, symbols, callback):
		manager = self.setupWebsocket()
		streams = []
		for coin in symbols:
			streams.append(DepthCacheManager(self.client, coin + "USDT", callback, bm=manager, ws_interval=30))
		return streams

	# return the current coin price
	def getCoinPrice(self, coin):
		for sym in (self.client.get_all_tickers()):
			if sym['symbol'] == coin:
				return (sym['price'])

	# get all orders for a coin
	def getCoinOrder(self, coin, amount):
		return self.client.get_all_orders(coin=coin, limit=amount)

	#get current spending limit
	def getUSD(self):
		return float(self.client.get_asset_balance(asset='USD')['free'])

	#get current coin holding
	def getCoinBalance(self, coin):
		return self.client.get_asset_balance(asset=coin)

	#returns a list of what I own
	def getAccountBalances(self):
		coins = []
		for coin in self.client.get_account()['balances']:
			if float(coin['free']) > 0 or float(coin['locked']) > 0:
				coins.append(coin)
		return coins

	#gets assets, asset totals, and totalBalance
	def getAssetPrices(self):
		owned = (self.getAccountBalances())
		for x in owned:
			asset = x['asset']
			if asset != 'USD': 
				price = float((self.getCoinPrice(f"{x['asset']}USD")))
				total = (float(x['free']) + float(x['locked'])) * price
				x['price'] = price
				x['total'] = total
		return owned

	# get all information about a coin
	def getCoinInfo(self, coin):
		return self.client.get_symbol_info(coin)

	# get the minimum amount of coin that can be purchased and the increments
	def getCoinPrecision(self, coin):
		return self.client.get_symbol_info(coin)['baseAssetPrecision']

	# get our current buying power
	def getPower(self):
		return self.getUSD()

	# buy a coin at the current market value
	def buyMarket(self, coin, amount):
		return self.client.order_market_buy(symbol=coin, quantity=amount)

	# sell a coin at the current market value
	def sellMarket(self, coin, amount):
		return self.client.order_market_sell(symbol=coin, quantity=amount)

	# sell a coin at the current market value
	def sellLimit(self, coin, amount, limit):
		info = self.getCoinInfo(coin)
		quotePrecision = int(info['quotePrecision'])
		limit = round(limit, quotePrecision - 2)
		return self.client.order_limit_sell(symbol=coin, quantity=amount, price=limit)

	# place a stoploss
	def stopLoss(self, coin, stop, limit, position):
		multiplierUp = 0
		multiplierDown = 0
		
		info = self.getCoinInfo(coin)

		quotePrecision = int(info['quotePrecision'])

		for filt in info['filters']:
			if filt['filterType'] == "PERCENT_PRICE":
				multiplierUp = float(filt['multiplierUp'])
				multiplierDown = float(filt['multiplierDown'])

		currentPrice = float(self.getCoinPrice(coin))

		upPrice = currentPrice * multiplierUp
		downPrice = currentPrice * multiplierDown

		stoper = round(stop, quotePrecision - 2)
		limiter = round(limit, quotePrecision - 2)

		print(f"up {upPrice}")
		print(f"down {downPrice}")
		print(f"stop {stoper}")
		print(f"limit {limiter}")

		if stoper > upPrice:
			print("TOHIGH")
			return None
		if stoper < downPrice:
			print("TOLOW")
			return None

		if limiter > upPrice:
			print("TOHIGH")
			return None
		if limiter < downPrice:
			print("TOLOW")
			return None

		output  = self.client.create_order(symbol=coin, 
			timeInForce='GTC',
			type='STOP_LOSS_LIMIT', 
			quantity=position, 
			side="sell", 
			price = limiter, 
			stopPrice=stoper)
		return output

	#test order will return {} if great success
	def testOrder(self, coin, act, amount):
		print(self.client.create_test_order( 
			symbol=coin, side=act, 
			type=ORDER_TYPE_MARKET,
			quantity=amount))

	# check the status of an order
	def getSellAmount(self, coin, order):
		order = self.client.get_order(symbol=coin, origClientOrderId=order)
		#add logic here for complete
		return round(float(order['cummulativeQuoteQty']), 2)
		

	def checkStatus(self, coin, order):
		order = self.client.get_order(symbol=coin, origClientOrderId=order)
		#add logic here for complete
		return order['status']


	# cancel an order that might get hung
	def cancelOrder(self, coin, order):
		return self.client.cancel_order(symbol=coin,origClientOrderId=order)

	def getBook(self):
		return self.client.get_orderbook_tickers()

	def getAssets(self):
		return self.client.get_account()

candlestick_patterns = {
    'CDL3BLACKCROWS':'Three Black Crows', # highly reliable http://thepatternsite.com/ThreeBlackCrows.html
    'CDL3LINESTRIKE':'Three-Line Strike', # highly reliable http://thepatternsite.com/ThreeLineStrikeBull.html
    'CDL3OUTSIDE':'Three Outside Up/Down', # good for both http://thepatternsite.com/ThreeOutsideUp.html
    'CDL3STARSINSOUTH':'Three Stars In The South', # reversal, but will not move up http://thepatternsite.com/ThreeStarsSouth.html
    'CDLABANDONEDBABY':'Abandoned Baby', # moderate performance, http://thepatternsite.com/AbandonBabyBull.html
    'CDLBELTHOLD':'Belt-hold', # moderate perofmance, http://thepatternsite.com/BeltHoldBull.html
    'CDLBREAKAWAY':'Breakaway', # reliable at star of downtrend, http://thepatternsite.com/BearBreakaway.html
    'CDLDOJISTAR':'Doji Star', # good performance, http://thepatternsite.com/EveningDojiStar.html
    'CDLENGULFING':'Engulfing Pattern', # need to use with something else, http://thepatternsite.com/BullEngulfing.html
    'CDLEVENINGDOJISTAR':'Evening Doji Star', # moderate performance, http://thepatternsite.com/EveningDojiStar.html
    'CDLHAMMER':'Hammer', # moderant performance http://thepatternsite.com/Hammer.html
    'CDLINVERTEDHAMMER':'Inverted Hammer', # possible use with other things, http://thepatternsite.com/HammerInv.html
    'CDLMATCHINGLOW':'Matching Low', # use with something else, http://thepatternsite.com/MatchingLow.html
    'CDLMATHOLD':'Mat Hold', # use with something else, http://thepatternsite.com/MatHold.html
    'CDLMORNINGDOJISTAR':'Morning Doji Star', # very good, http://thepatternsite.com/MorningDojiStar.html
    'CDLMORNINGSTAR':'Morning Star', # reliable, http://thepatternsite.com/MorningStar.html
    'CDLPIERCING':'Piercing Pattern', # reliable, http://thepatternsite.com/Piercing.html
    'CDLRISEFALL3METHODS':'Rising/Falling Three Methods', # highly reliable, http://thepatternsite.com/Falling3Methods.html
    'CDLSEPARATINGLINES':'Separating Lines', # highly reliable, http://thepatternsite.com/SeparateLinesBull.html
    'CDLSHOOTINGSTAR':'Shooting Star', # reliable, http://www.thepatternsite.com/ShootingStar.html
    'CDLSTICKSANDWICH':'Stick Sandwich', # reliable, http://thepatternsite.com/StickSandwich.html
    'CDLTAKURI':'Takuri (Dragonfly Doji with very long lower shadow)', # good bullish reversal, http://thepatternsite.com/TakuriLine.html
    'CDLUNIQUE3RIVER':'Unique 3 River', #, reliable, http://thepatternsite.com/Unique3RiverBottom.html
    'CDLUPSIDEGAP2CROWS':'Upside Gap Two Crows',
    'CDLXSIDEGAP3METHODS':'Upside/Downside Gap Three Methods' # reliable, http://thepatternsite.com/DownGap3Methods.html
}

us_coins = [
	'ADAUSDT',
	'ATOMUSDT',
	'BANDUSDT',
	'BATUSDT',
	'BCHUSDT',
	'BNBUSDT',
	'BTCUSDT',
	'COMPUSDT',
	'DASHUSD',
	'DOGEUSDT',
	'EGLDUSDT',
	'ENJUSD',
	'EOSUSD',
	'ETHUSDT',
	'HBARUSD',
	'HNTUSDT',
	'ICXUSD',
	'IOTAUSD',
	'KNCUSDT',
	'LINKUSD',
	'LTCUSDT',
	'MANAUSD',
	'MATICUSD',
	'MKRUSDT',
	'NANOUSD',
	'NEOUSDT',
	'OMGUSD',
	'ONEUSDT',
	'ONTUSDT',
	'OXTUSDT',
	'PAXGUSDT',
	'QTUMUSDT',
	'REPUSD',
	'RVNUSD',
	'SOLUSDT',
	'STORJUSDT',
	'UNIUSDT',
	'VETUSDT',
	'WAVESUSD',
	'XLMUSDT',
	'XTZUSD',
	'ZECUSD',
	'ZENUSD',
	'ZILUSD',
	'ZRXUSDT'
]