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
            names=['coin', 'capital', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime'])
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
        with open(f"logdata/{destination}.txt", "a") as f:
            f.write(message)
            f.write("\n")

    def saveCoinBuyData(self, coin, price, amount, setcap=0.0, setupdatetime=180):
        df = self.readConfig()
        if setcap > 0:
            df.at[coin, 'capital'] = setcap
        df.at[coin, 'starting'] = price
        df.at[coin, 'autobought'] = amount
        df.at[coin, 'limit'] = price * df.at[coin, 'takeprofit']
        df.at[coin, 'updatetime'] = setupdatetime
        self.setCoinConfigData(df)


    def saveCoinLimitData(self, coin, price, limit, setupdatetime=180):
        df = self.readConfig()
        df.at[coin, 'currentPrice'] = price
        df.at[coin, 'limit'] = limit

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
            timeout = 5
            time.sleep(2)
            #check a couple of times to make sure we are selling
            while status != 'FILLED':
                if timeout > 5:
                    timeout = 0
                    self.candles.cancelOrder(coin, orderID)
                status = self.candles.checkStatus(coin, orderID)
                timeout += 1
                time.sleep(2)

            # save the data for analysis later and reset the bot coin's config
            self.logit(f"SELLING DUE TO TAKEPROFIT {sellorder}", coin)
            sellprice = float(sellorder['fills'][0]['price']) * amount
            print(sellprice)
            self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)


    def runForever(self):
        while 1:
            self.masterTicker += 10
            df = self.readConfig()
            # loop over the contents of our config file
            for index, row in df.iterrows():
                # check to see if the bot has made a purchase
                position = float(row['autobought'])
                if position > 0:
                    currentPrice = self.getQuote(index)
                    # if the bot has bought, check the update time
                    updatetime = int(row['updatetime'])
                    if self.masterTicker % updatetime == 0:
                        #get the current price and check if it's above our current limit
                        currentLimit = float(row['limit'])
                        if currentPrice < currentLimit:
                            self.sellNow(index)
                        else:
                            # calculate a new limit based on our coin's config profile
                            newlimit = currentPrice*float(row['takeprofit'])
                            if newlimit > currentLimit:
                                self.saveCoinLimitData(index, currentPrice, newlimit)
                    self.logit(f"{row.starting}, {currentPrice}, {row.limit}", index)
            time.sleep(10)

connector = CandleConnector()

while 1:
    #TODO add away to enable testing
    #connector.saveCoinBuyData("ADAUSD", float(connector.getQuote("ADAUSD")), 20)
    #TODO add a web interface that will display the current buying data
    connector.runForever()