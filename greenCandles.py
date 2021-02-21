#!/usr/bin/python3

from binance.client import Client
from binance.enums import *
import time
from binance.websockets import BinanceSocketManager
import pandas as pd
import sys
sys.path.append('../')
import clientConfig

from filelock import Timeout, FileLock

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

#this will handle the connection to binace
class BinaceConnector():
	def __init__(self):
		self.client = Client(clientConfig.api_key, clientConfig.api_secret, tld='us')

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

	#test order will return {} if great success
	def testOrder(self, coin, act, amount):
		print(self.client.create_test_order( 
			symbol=coin, side=act, 
			type=ORDER_TYPE_MARKET,
			quantity=amount))

	# check the status of an order
	def checkStatus(self, coin, order):
		order = self.client.get_order(symbol=coin, origClientOrderId=order)
		#add logic here for complete
		return order['status']

	# cancel an order that might get hung
	def cancelOrder(self, coin, order):
		return client.cancel_order(symbol=coin,origClientOrderId=order)


#this class is the top layer for the monitor and interface
# class CandleConnector():
# 	def __init__(self):
# 		self.lock = FileLock("config.csv.lock")
# 		# make dict here that stores the amount for each coin
# 		self.config = "config.csv"
# 		self.candles = BinaceConnector()

# 	def readConfig(self):
# 		self.lock.acquire()
# 		df = pd.read_csv(self.config,encoding='utf8', delimiter=',' , 
# 			names=['coin', 'capital', 'starting', 'limit', 'currentPrice', 'autobought', 'updatetime'])
# 		self.lock.release()
# 		df.set_index('coin', inplace=True)
# 		return df


# 	#get the current config
# 	def getCoinConfigData(self, coin):
# 		df = self.readConfig()
# 		return df.loc[coin]

# 	#save a new copy of the config
# 	def setCoinConfigData(self, df):
# 		self.lock.acquire()
# 		df.to_csv(f'config.csv', mode='w', header=False, index=True)
# 		self.lock.release()

# 	def getAutoBoughtAmount(self, coin):
# 		return float(self.getCoinConfigData(coin)['autobought'])

# 	# helper for buying a number of coins at current price
# 	def orderNumber(self, coin, number):
# 		return (self.candles.buyMarket(coin, number))

# 	# gives you a quote for a coin
# 	def getQuote(self, coin):
# 		return float(self.candles.getCoinPrice(coin))

# 	# set an order for an number amount
# 	def orderAmount(self, coin, amount):
# 		return (self.candles.order_buy_crypto_by_price(coin, amount))

# 	# write out to a log file
# 	def logit(self, message, destination):
# 		with open(f"logdata/{destination}.txt", "a") as f:
# 			f.write(message)
# 			f.write("\n")

# 	def saveCoinBuyData(self, coin, price, amount, setcap=None):
# 		df = self.readConfig()
# 		if setcap is not None:
# 			df.at[coin, 'capital'] = setcap
# 		df.at[coin, 'starting'] = price
# 		df.at[coin, 'autobought'] = amount
# 		df.at[coin, 'takeprofit'] = .99
# 		df.at[coin, 'limit'] = price * .98
# 		self.setCoinConfigData(df)

# 	# check to see how much can be purchased with the current capital
# 	# then purchase that amount of coins
# 	def buyNow(self, coin, strat=None):
# 		price = self.getQuote(coin)
# 		#TODO add logic that allows for multiple strategies that will 
#         #allow for different allocations of the starting capital
# 		BOUGHT = float(self.getCoinConfigData(coin)['capital'] / self.getQuote(coin))
# 		minOrder = None
# 		minNot = None

# 		#grab the trading rules for the coin
# 		for filt in (self.candles.getCoinInfo(coin)['filters']):
# 			if filt['filterType'] == "LOT_SIZE":
# 				minOrder = float(filt['minQty'])
# 			if filt['filterType'] == 'MIN_NOTIONAL':
# 				minNot = float(filt['minNotional'])
# 		mod = BOUGHT % minOrder

# 		#make sure the amount we are buying is standardized for Binance
# 		if mod:
# 			BOUGHT = BOUGHT - mod


# 		if (BOUGHT * price) > minNot:
# 			order = self.orderNumber(coin, BOUGHT)
# 			self.saveCoinBuyData(coin, price, BOUGHT)
# 			self.logit(f"BUYING {order}", coin)
# 		else:
# 			BOUGHT = None
# 			self.logit(f"Failed to buy {BOUGHT}, {coin}. Due minNotional of {minNot}", coin)
# 		return BOUGHT

# 	#sell an amount at current price
# 	def sellNow(self, coin):
# 		#get the amount the bot bought
# 		amount = self.getAutoBoughtAmount(coin)
# 		if amount > 0:
# 			# self.candles.testOrder(coin, SIDE_SELL, amount)
# 			sellorder = self.candles.sellMarket(coin, amount)
# 			orderID = sellorder['clientOrderId']
# 			status = self.candles.checkStatus(coin, orderID)
# 			timeout = 5
# 			time.sleep(2)
# 			#check a couple of times to make sure we are selling
# 			while status != 'FILLED':
# 				if timeout > 5:
# 					timeout = 0
# 					self.candles.cancelOrder(coin, orderID)
# 				status = self.candles.checkStatus(coin, orderID)
# 				timeout += 1
# 				time.sleep(2)

# 			# save the data for analysis later and reset the bot coin's config
# 			self.logit(f"SELLING DUE TO STRAT {sellorder}", coin)
# 			sellprice = float(sellorder['fills'][0]['price']) * amount
# 			print(sellprice)
# 			self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)


# connector = CandleConnector()

# coin = "ETCUSD"
# #for quick trades let's print the price somehow
# print(connector.buyNow(coin))
# input("Enter when ready to sell ") 
# print(connector.sellNow(coin))
