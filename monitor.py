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
        self.masterTicker = -60

    def readConfig(self):
        self.lock.acquire()
        df = pd.read_csv(self.config,encoding='utf8', delimiter=',' , 
            names= ['coin', 'capital', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime', 'orderid', 'takeProfitAmount', 'takeProfitOrder', 'delta'])
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
        df.at[coin, 'delta'] = delta -180
        self.setCoinConfigData(df)

    def updateOrder(self, coin, order):
        df = self.readConfig()
        df.at[coin, 'orderid'] = order
        self.setCoinConfigData(df)


    #sell an amount at current price
    def sellNow(self, coin):
        #get the amount the bot bought
        amount = self.getAutoBoughtAmount(coin)
        print(f"found {amount}")
        if amount > 0:
            print(f"selling")
            sellorder = self.candles.sellMarket(coin, amount)
            time.sleep(1)
            # save the data for analysis later and reset the bot coin's config
            self.logit(f"SELLING DUE TO TAKEPROFIT {sellorder}", "logger")
            #need to check to make sure we did sell before we save this
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
                    currentOrder = row['orderid']
                    updatetime = int(row['updatetime'])
                    delta = self.masterTicker % updatetime
                    if delta== 0:
                        #get the current price and check if it's above our current limit
                        currentLimit = float(row['limit'])
                        if currentPrice < currentLimit:
                            print("checking order")
                            if "none" not in currentOrder:
                                print("cancelOrder")
                                status = self.candles.checkStatus(coin, currentOrder)
                                if status != 'FILLED':
                                    self.candles.cancelOrder(coin, currentOrder)
                                    time.sleep(.3)
                                    print(f"selling because price {currentPrice} < limit {currentLimit}")
                                    self.sellNow(coin)
                            else:
                                self.sellNow(coin)
                        else:
                            # calculate a new limit based on our coin's config profile
                            newlimit = currentPrice*float(row['takeprofit'])
                            print(f"new limit {newlimit}")
                            if newlimit > currentLimit:
                                print(f"new limit > {currentLimit}")
                                self.saveCoinLimitData(coin, currentPrice, newlimit)

                    starting = float(row['starting'])
                    # check to see if a stop loss order has been placed
                    if "none" not in currentOrder:
                        print(f"order {currentOrder} is", end = " ")
                        status = self.candles.checkStatus(coin, currentOrder)
                        if status == 'FILLED':
                            print("FILLED so close")
                            sellprice = float(status['fills'][0]['price']) * row['autobought']
                            self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)
                        print("open")
                    # if stop loss has not been placed, and we are in profit attempt to atleast cover our fees
                    elif currentPrice > starting + (starting * 0.005):
                        print("made our money back placing limit order")
                        #save this order and save to config`
                        order = connector.candles.stopLoss(coin, 
                            stop=(starting + (starting * (2 * .0008))), 
                            limit=(starting + (starting * (2 * .00076))), 
                            position=position)['clientOrderId']
                        self.updateOrder(coin, order)

                    self.updateDelta(coin, delta, currentPrice)
                    self.logit(f"{self.masterTicker}, {row.starting}, {currentPrice}, {row.limit}", coin)
            self.echoCurrentTick()
            time.sleep(60)

connector = CandleConnector()

while 1:
    #TODO add away to enable testing
    #connector.saveCoinBuyData("ADAUSD", float(connector.getQuote("ADAUSD")), 20)
    connector.runForever()