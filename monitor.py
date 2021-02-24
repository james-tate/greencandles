#!/usr/bin/python3


#TODO change polling to websocket design

import time
import pandas as pd
import greenCandles as candles
from filelock import Timeout, FileLock

class CandleConnector():
    def __init__(self):
        self.lock = FileLock("config.csv.lock")
        # make dict here that stores the amount for each coin
        self.config = "config.csv"
        self.candles = candles.BinaceConnector()
        self.masterTicker = 0

    def readConfig(self):
        self.lock.acquire()
        df = pd.read_csv(self.config,encoding='utf8', delimiter=',' , 
            names=['coin', 'currentcap', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime', 'orderid', 'takeProfitAmount', 'takeProfitOrder' 'delta'])
        self.lock.release()
        df.set_index('coin', inplace=True)
        return df

    #get the current config
    def getCoinConfigData(self, coin):
        df = self.readConfig()
        return df.loc[coin]

    #save a new copy of the config
    def setCoinConfigData(self, df):
        self.lock.acquire()
        df.to_csv(f'config.csv', mode='w', header=False, index=True)
        self.lock.release()

    def getAutoBoughtAmount(self, coin):
        return float(self.getCoinConfigData(coin)['autobought'])

    # helper for buying a number of coins at current price
    def orderNumber(self, coin, number):
        return (self.candles.buyMarket(coin, number))

    # gives you a quote for a coin
    def getQuote(self, coin):
        return float(self.candles.getCoinPrice(coin))

    # write out to a log file
    def logit(self, message, destination):
        with open(f"testData/{destination}.txt", "a") as f:
            f.write(message)
            f.write("\n")

    def saveCoinBuyData(self, coin, price, amount, setcap=0.0, setupdatetime=180, order="none"):
        df = self.readConfig()
        if setcap > 0:
            df.at[coin, 'capital'] = setcap
        df.at[coin, 'starting'] = price
        df.at[coin, 'autobought'] = amount
        df.at[coin, 'limit'] = price * df.at[coin, 'takeprofit']
        df.at[coin, 'updatetime'] = setupdatetime
        df.at[coin, 'orderid'] = order
        self.setCoinConfigData(df)


    def saveCoinLimitData(self, coin, price, limit, setupdatetime=180,):
        df = self.readConfig()
        df.at[coin, 'currentPrice'] = price
        df.at[coin, 'limit'] = limit
        self.setCoinConfigData(df)

    def updateDelta(self, coin, delta, price):
        df = self.readConfig()
        df.at[coin, 'currentPrice'] = price
        df.at[coin, 'delta'] = delta
        self.setCoinConfigData(df)

    def updateOrder(self, coin, order):
        df = self.readConfig()
        df.at[coin, 'orderid'] = order
        self.setCoinConfigData(df)


    #sell an amount at current price
    def sellNow(self, coin):
        #get the amount the bot bought
        amount = self.getAutoBoughtAmount(coin)
        if amount > 0:
            # self.candles.testOrder(coin, SIDE_SELL, amount)
            sellorder = self.candles.sellMarket(coin, amount)
            orderID = sellorder['clientOrderId']
            status = self.candles.checkStatus(coin, orderID)
            # save the data for analysis later and reset the bot coin's config
            self.logit(f"SELLING DUE TO TAKEPROFIT {sellorder}", "logger")
            sellprice = float(sellorder['fills'][0]['price']) * amount
            print(sellprice)
            self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)

    def echoCurrentTick(self):
        with open('tick', 'w') as f:
            f.write(f"{self.masterTicker}")

    def runForever(self):
        while 1:
            self.masterTicker += 60
            df = self.readConfig()
            # loop over the contents of our config file
            tickers = self.candles.getBook()
            for coin, row in df.iterrows():
                # check to see if the bot has made a purchase
                position = float(row['autobought'])
                if position > 0:
                    for x in tickers:
                        if coin == x['symbol']:
                            currentPrice = float(x['bidPrice'])
                    # if the bot has bought, check the update time
                    updatetime = int(row['updatetime'])
                    delta = self.masterTicker % updatetime
                    if delta== 0:
                        #get the current price and check if it's above our current limit
                        currentLimit = float(row['limit'])
                        if currentPrice < currentLimit:
                            if "none" not in row['orderid']:
                                self.candles.cancelOrder(coin, row['orderid'])
                                time.sleep(.3)
                            self.sellNow(coin)
                        else:
                            # calculate a new limit based on our coin's config profile
                            newlimit = currentPrice*float(row['takeprofit'])
                            if newlimit > currentLimit:
                                self.saveCoinLimitData(coin, currentPrice, newlimit)

                    # check to see if a stop loss order has been placed
                    if "none" not in row['orderid']:
                        status = self.candles.checkStatus(coin, row['orderid'])
                        if status == 'FILLED':
                            sellprice = float(status['fills'][0]['price']) * row['autobought']
                            self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)
                    # if stop loss has not been placed, and we are in profit attempt to atleast cover our fees
                    elif currentPrice > row['starting'] + (float(row['starting']) * (2 * 0.001)):
                        #save this order and save to config
                        order = connector.candles.stopLoss(coin, 
                            stop=(row['starting'] + (row['starting'] * (2 * .0008))), 
                            limit=(row['starting'] + (row['starting'] * (2 * .00076))), 
                            position=position)['clientOrderId']


                    self.updateDelta(coin, delta, currentPrice)
                    self.logit(f"{self.masterTicker}, {row.starting}, {currentPrice}, {row.limit}", coin)
            self.echoCurrentTick()
            time.sleep(60)

connector = CandleConnector()

while 1:
    #TODO add away to enable testing
    #connector.saveCoinBuyData("ADAUSD", float(connector.getQuote("ADAUSD")), 20)
    connector.runForever()