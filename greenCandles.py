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
		return self.client.cancel_order(symbol=coin,origClientOrderId=order)

	def getBook(self):
		return self.client.get_orderbook_tickers()