#!/usr/bin/python3

from flask import Flask, request, render_template
import json
from threading import Thread
import time
import greenCandles as candles
import pandas as pd
import threading
import plotly
import plotly.graph_objects as go
from filelock import Timeout, FileLock
from datetime import datetime
import os
import pathlib

app = Flask(__name__)

#this class is the top layer for the monitor and interface
class CandleConnector():
    def __init__(self):
        self.lock = FileLock("config.csv.lock")
        # make dict here that stores the amount for each coin
        self.config = "config.csv"
        self.candles = candles.BinaceConnector()

    def readConfig(self):
        self.lock.acquire()
        df = pd.read_csv(self.config,encoding='utf8', delimiter=',' , 
            names=['coin', 'capital', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime', 'orderid'])
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

    def getBuyPower(self):
        return float(self.candles.getUSD())

    # set an order for an number amount
    def orderAmount(self, coin, amount):
        return (self.candles.order_buy_crypto_by_price(coin, amount))

    # write out to a log file
    def logit(self, message, destination):
        with open(f"testData/{destination}.txt", "a") as f:
            f.write(message)
            f.write("\n")

    def saveCoinBuyData(self, coin, price, amount, setcap=None, setupdatetime=180, order="0"):
        df = self.readConfig()
        if setcap is not None:
            df.at[coin, 'capital'] = setcap
        df.at[coin, 'starting'] = price
        df.at[coin, 'autobought'] = amount
        df.at[coin, 'limit'] = price * df.at[coin, 'takeprofit']
        df.at[coin, 'updatetime'] = setupdatetime
        df.at[coin, 'orderid'] = order
        self.setCoinConfigData(df)

    # check to see how much can be purchased with the current capital
    # then purchase that amount of coins
    def buyNow(self, coin, strat=None):
        coinsCapital = self.getCoinConfigData(coin)['capital']
        avalFunds = self.getBuyPower()
        if (coinsCapital > avalFunds) is True:
            return 0

        if float(self.getCoinConfigData(coin)['position']) > 0:
            return 0

        price = self.getQuote(coin)
        #TODO add logic that allows for multiple strategies that will 
        #allow for different allocations of the starting capital
        BOUGHT = float(coinsCapital / self.getQuote(coin))
        minOrder = None
        minNot = None   
        print(BOUGHT)
        #grab the trading rules for the coin
        for filt in (self.candles.getCoinInfo(coin)['filters']):
            if filt['filterType'] == "LOT_SIZE":
                minOrder = float(filt['minQty'])
            if filt['filterType'] == 'MIN_NOTIONAL':
                minNot = float(filt['minNotional'])
        mod = BOUGHT % minOrder

        #make sure the amount we are buying is standardized for Binance
        if mod:
            BOUGHT = BOUGHT - mod

        #this needs to get the perciesion from the filter

        BOUGHT = round(BOUGHT, int(self.getCoinInfo(coin)['quotePrecision']))
        print(BOUGHT)
        if (BOUGHT * price) > minNot:
            order = self.orderNumber(coin, BOUGHT)
            self.saveCoinBuyData(coin, price, BOUGHT)
            self.logit(f"BUYING {order}", "logger")
            #reset our coin data so we can have a current graph
            file = pathlib.Path(f"testData/{coin}.txt")
            if file.exists ():
                os.rename(f"testData/{coin}.txt", f"testData/{coin}{datetime.now()}.txt")
        else:
            BOUGHT = None
            self.logit(f"Failed to buy {BOUGHT}, {coin}. Due minNotional of {minNot}", "logger")
        return BOUGHT

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
            self.logit(f"SELLING DUE TO STRAT {sellorder}", "logger")
            sellprice = float(sellorder['fills'][0]['price']) * amount
            print(sellprice)
            self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)

    def doit(self, coin, action):
        self.logit(f"buysell {action}", "logger")
        self.logit(f"symbol {coin}", "logger")
        if action == 'sell':
            self.sellNow(coin)
        if action == 'buy':
            self.buyNow(coin)



# =========================================================================
connector = CandleConnector()

@app.route('/tester')
def home():
    return "working"

@app.route('/stratAccept', methods=['POST'])
#message should be sent to this in JSON format
# example:
#       {"symbol": "ETHUSD", "action": "sell"}
def stratAccept():
    try:
        incoming = request.json
        print(incoming)
        symbol = incoming['symbol']
        action = incoming['action']
        print(symbol)
        connector.doit(symbol, action)
        return ""
    except Exception as e:
        print(e)
        return ""

@app.route('/monitorView')
def monitorView():
    #TODO change this to templete
    currentTick = 0
    with open('tick', 'r') as f:
        currentTick = f.read()
    book = connector.candles.getBook()
    page = "<!DOCTYPE html> <html> <meta http-equiv=\"refresh\" content=\"10\" /><body>"
    page += "<style>\
            table {\
                font-size: .8em;\
                font-family: arial, sans-serif;\
                border-collapse: collapse;\
                width: 300%;\
            }\
            td, th {\
                width: 100px;\
                border: 1px solid #dddddd;\
                text-align: center;\
                padding: 1px;\
            }\
            tr:nth-child(even) {\
                background-color: #dddddd;\
            }\
            </style>"
    page += '<p id="currentTime"></p>'
    page += '<p id="update"></p>'
    df = connector.readConfig()
    page += f'<h3>CURRENT TICK {currentTick}</h3>'
    page += '<table style="width:60%">'
    page += f'<tr style=\"height:50px\"><th> </th><th>capital</th><th>starting</th><th>limit</th>\
    <th>currentPrice</th><th>position</th><th>takeprofit</th><th>updatetime</th><th>askPrice</th>\
    <th>askQty</th><th>bidPrice</th><th>bidQty</th></tr>'
    for coin, row in df.iterrows():
        askPrice = 0
        askQty = 0
        binPrice = 0
        bidQty = 0
        for x in book:
            if coin == x['symbol']:
                askPrice = float(x['askPrice'])
                askQty = float(x['askQty'])
                binPrice = float(x['bidPrice'])
                bidQty = float(x['bidQty'])
        page += f"<tr><td style=\"font-weight:bold\"><a href=\"/graphLimit?coin={coin}\">{coin}</a></td>\
            <td>{row['capital']}</td><td>{row['starting']}</td>\
            <td>{row['limit']}</td><td>{row['currentPrice']}</td><td>{row['autobought']}</td>\
            <td>{row['takeprofit']}</td><td>{row['updatetime']}</td><td>{askPrice}</td>\
            <td>{askQty}</td><td>{binPrice}</td><td>{bidQty}</td></tr>"
    page += '</table>'
    page += f'<script> var myVar = setInterval(myTimer, 1000); \
        function myTimer() {{ \
            var d = new Date();\
            var t = d.toLocaleTimeString(); \
            document.getElementById("currentTime").innerHTML = t;}}\
        </script>'
    page += '</body> </html>'

    return page

#graph the limit to etc here
@app.route('/graphLimit', methods=['GET'])
def limitGraph():

    df = pd.read_csv(f'testData/{request.args.get("coin")}.txt' ,encoding='utf8', delimiter=',' , names=['start', 'price', 'limit',])
    fig = go.Figure()
    fig.add_traces(go.Scatter(x=df.index, y = df['price'], mode = 'lines', name="price"))
    fig.add_traces(go.Scatter(x=df.index, y = df['start'], mode = 'lines', name="start"))
    fig.add_traces(go.Scatter(x=df.index, y = df['limit'], mode = 'lines', name="limit"))
    plotly.offline.plot(fig, filename='templates/name.html')
    # bar = create_plot()
    return render_template("name.html")

@app.route('/purchased')
def purchased():
    currentTick = 0
    with open('tick', 'r') as f:
        currentTick = f.read()
    book = connector.candles.getBook()
    page = "<style>\
            table {\
                font-size: .8em;\
                font-family: arial, sans-serif;\
                border-collapse: collapse;\
                width: 300%;\
            }\
            td, th {\
                width: 100px;\
                border: 1px solid #dddddd;\
                text-align: center;\
                padding: 1px;\
            }\
            tr:nth-child(even) {\
                background-color: #dddddd;\
            }\
            </style>"
    df = connector.readConfig()
    page += f'<h3>CURRENT TICK {currentTick}</h3>'
    page += '<table style="width:60%">'
    page += f'<tr style=\"height:50px\"><th> </th><th>capital</th><th>starting</th><th>limit</th>\
    <th>currentPrice</th><th>position</th><th>takeprofit</th><th>updatetime</th><th>askPrice</th>\
    <th>askQty</th><th>bidPrice</th><th>bidQty</th></tr>'
    for coin, row in df.iterrows():
        position = float(row['autobought'])
        if position > 0:
            askPrice = 0
            askQty = 0
            binPrice = 0
            bidQty = 0
            for x in book:
                if coin == x['symbol']:
                    askPrice = float(x['askPrice'])
                    askQty = float(x['askQty'])
                    binPrice = float(x['bidPrice'])
                    bidQty = float(x['bidQty'])
            page += f"<tr><td style=\"font-weight:bold\">{coin}</td><td>{row['capital']}</td><td>{row['starting']}</td>\
                <td>{row['limit']}</td><td>{row['currentPrice']}</td><td>{row['autobought']}</td>\
                <td>{row['takeprofit']}</td><td>{row['updatetime']}</td><td>{askPrice}</td>\
                <td>{askQty}</td><td>{binPrice}</td><td>{bidQty}</td></tr>"
    page += '</table>'

    return page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11337, debug=True)