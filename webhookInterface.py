#!/usr/bin/python3

from flask import Flask, request, render_template
import json
from threading import Thread
import time
import greenCandles as candles
from greenCandles import candlestick_patterns
import pandas as pd
import threading
import plotly
import plotly.graph_objects as go
from filelock import Timeout, FileLock
from datetime import datetime
import talib
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
            names=['coin', 'capital', 'starting', 'limit', 'currentPrice', 'autobought', 'takeprofit', 'updatetime', 'orderid', 'takeProfitAmount', 'takeProfitOrder', 'delta'])
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

    def saveCoinBuyData(self, coin, price, amount, setcap=None, setupdatetime=180, order="none"):
        df = self.readConfig()
        if setcap is not None:
            df.at[coin, 'capital'] = setcap
        df.at[coin, 'starting'] = price
        df.at[coin, 'autobought'] = amount
        df.at[coin, 'limit'] = price * df.at[coin, 'takeprofit']
        df.at[coin, 'updatetime'] = setupdatetime
        df.at[coin, 'orderid'] = order
        self.setCoinConfigData(df)

    def saveCoinLimitBuyData(self, coin, price, amount, order):
        df = self.readConfig()
        df.at[coin, 'starting'] = price
        df.at[coin, 'takeProfitAmount'] = amount
        df.at[coin, 'takeProfitOrder'] = order
        self.setCoinConfigData(df)

    # check to see how much can be purchased with the current capital
    # then purchase that amount of coins
    def buyForProfit(self, coin, strat=None):
        coinsCapital = self.getCoinConfigData(coin)['capital']
        avalFunds = self.getBuyPower()
        print(f"capital {coinsCapital} above funds {avalFunds} is {coinsCapital > avalFunds}")
        if (coinsCapital > avalFunds):
            return 0
        if float(self.getCoinConfigData(coin)['autobought']) > 0:
            return 0

        price = self.getQuote(coin)
        #TODO add logic that allows for multiple strategies that will 
        #allow for different allocations of the starting capital
        bought = float(coinsCapital / self.getQuote(coin))
        minOrder = None
        minNot = None   
        print(bought)
        #grab the trading rules for the coin
        for filt in (self.candles.getCoinInfo(coin)['filters']):
            if filt['filterType'] == "LOT_SIZE":
                minOrder = float(filt['minQty'])
            if filt['filterType'] == 'MIN_NOTIONAL':
                minNot = float(filt['minNotional'])
        mod = bought % minOrder

        #make sure the amount we are buying is standardized for Binance
        if mod:
            bought = bought - mod

        #this needs to get the perciesion from the filter

        bought = round(bought, int(self.candles.getCoinInfo(coin)['quotePrecision']))
        print(bought)
        if (bought * price) > minNot:
            order = self.orderNumber(coin, bought)
            self.saveCoinBuyData(coin, price, bought)
            self.logit(f"BUYING {order}", "logger")
            #reset our coin data so we can have a current graph
            file = pathlib.Path(f"testData/{coin}.txt")
            if file.exists ():
                os.rename(f"testData/{coin}.txt", f"testData/{coin}{datetime.now()}.txt")
        else:
            bought = None
            self.logit(f"Failed to buy {bought}, {coin}. Due minNotional of {minNot}", "logger")
        return bought, price

    # check to see how much can be purchased with the current capital
    # then purchase that amount of coins
    def buyForLimit(self, coin, strat=None):
        #TODO seperate the capital out so we can run both at the same time
        coinsCapital = float(self.getCoinConfigData(coin)['capital'])
        avalFunds = self.getBuyPower()
        prevoiusID = self.getCoinConfigData(coin)['takeProfitOrder']
        print(avalFunds)
        print(coinsCapital)
        if (coinsCapital > avalFunds):
            print("no money")
            return None
        #test here to see if previous order has been filled
        previousOrder = self.getCoinConfigData(coin)['takeProfitOrder']
        print(f"Prevoius {previousOrder}")
        if previousOrder != "none":
            print("previous order")
            status = self.candles.checkStatus(coin, previousOrder)
            #if previous status has been filled. We need to save the winnings to new capital
            print(f"status {status}")
            if 'FILLED' != status:
                print("previous has not filled yet")
                return None
            print("previous has been filled so let's buy more")

        price = self.getQuote(coin)
        #TODO add logic that allows for multiple strategies that will 
        #allow for different allocations of the starting capital
        bought = float(coinsCapital / self.getQuote(coin))
        minOrder = None
        minNot = None   
        print(bought)
        #grab the trading rules for the coin
        for filt in (self.candles.getCoinInfo(coin)['filters']):
            if filt['filterType'] == "LOT_SIZE":
                minOrder = float(filt['minQty'])
            if filt['filterType'] == 'MIN_NOTIONAL':
                minNot = float(filt['minNotional'])
        mod = bought % minOrder

        #make sure the amount we are buying is standardized for Binance
        if mod:
            bought = bought - mod

        #this needs to get the perciesion from the filter
        bought = round(bought, int(self.candles.getCoinInfo(coin)['quotePrecision']))
        print(bought)
        if (bought * price) > minNot:
            order = self.orderNumber(coin, bought)
            self.logit(f"BUYING {order}", "logger")
            #reset our coin data so we can have a current graph
            file = pathlib.Path(f"testData/{coin}.txt")
            if file.exists ():
                os.rename(f"testData/{coin}.txt", f"testData/{coin}{datetime.now()}.txt")
            return order
        else:
            bought = None
            self.logit(f"Failed to buy {bought}, {coin}. Due minNotional of {minNot}", "logger")
        return None

    #sell an amount at current price
    def sellNow(self, coin):
        #get the amount the bot bought
        amount = self.getAutoBoughtAmount(coin)
        print(f"we have {amount}")
        if amount > 0:
            print(f"selling")
            #NEED TO CHECK TO SEE IF WE CURRNTLY HAVE AN ORDER
            orderID = self.getCoinConfigData(coin)['orderid']
            print(f"previous order {orderID}")
            if "none" not in orderid:
                print("cancelOrder")
                self.candles.cancelOrder(coin, orderid)
                time.sleep(.3)
            # self.candles.testOrder(coin, SIDE_SELL, amount)
            sellorder = self.candles.sellMarket(coin, amount)
            orderID = sellorder['clientOrderId']
            # save the data for analysis later and reset the bot coin's config
            self.logit(f"SELLING DUE TO STRAT {sellorder}", "logger")
            sellprice = float(sellorder['fills'][0]['price']) * amount
            print(sellprice)
            self.saveCoinBuyData(coin, 0, 0, setcap=sellprice)

    def doMaxProfit(self, coin, action):
        self.logit(f"buysell {action}", "logger")
        self.logit(f"symbol {coin}", "logger")
        if action == 'sell':
            self.sellNow(coin)
        if action == 'buy':
            self.buyForProfit(coin)

    def doTakeProfit(self, coin, action):
        self.logit(f"buysell limit {action}", "logger")
        self.logit(f"symbol limit {coin}", "logger")
        #add sell logic
        if action == 'buy':
            order = self.buyForLimit(coin)
            time.sleep(.5)
            if order is not None:
                price = float(order['fills'][0]['price'])
                limit = price * 1.01
                amount = float(order['fills'][0]['qty'])
                limit_order = self.candles.sellLimit(coin, amount, limit)
                self.saveCoinLimitBuyData(coin, price, limit, limit_order['clientOrderId'])
        elif action == 'sell':
            previousOrder = self.getCoinConfigData(coin)['takeProfitOrder']
            if previousOrder != "none":
                print("previous order")
                status = self.candles.checkStatus(coin, previousOrder)
                #if previous status has been filled. We need to save the winnings to new capital
                print(f"status {status}")
                if 'FILLED' != status:
                    print("previous has not filled yet so we gonna cancel")
                    self.candles.cancelOrder(coin, previousOrder)
                    time.sleep(.3)
                    self.sellNow(coin)
                    return None
                print("previous has been filled so nothing to do")


# =========================================================================
connector = CandleConnector()

@app.route('/tester')
def home():
    return "working"

#this endpoint longer term strategies that try to maximize the gains
@app.route('/maxProfit', methods=['POST'])
#message should be sent to this in JSON format
# example:
#       {"symbol": "ETHUSD", "action": "sell"}
def maxProfit():
    try:
        incoming = request.json
        print(incoming)
        symbol = incoming['symbol']
        action = incoming['action']
        print(symbol)
        connector.doMaxProfit(symbol, action)
        return ""
    except Exception as e:
        print(e)
        return ""

#this endpoint sets a take profit limit used for shorter,smaller, and more frequent trades.
@app.route('/takeProfit', methods=['POST'])
#message should be sent to this in JSON format
# example:
#       {"symbol": "ETHUSD", "action": "sell"}
def takeProfit():
    try:
        incoming = request.json
        print(incoming)
        symbol = incoming['symbol']
        action = incoming['action']
        print(symbol)
        connector.doTakeProfit(symbol, action)
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
    page = "<!DOCTYPE html> <html> <meta http-equiv=\"refresh\" content=\"60\" /><body>"
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
    <th>currentPrice</th><th>position</th><th>takeprofit</th><th>updatetime</th><th>delta</th><th>askPrice</th>\
    <th>askQty</th><th>bidPrice</th><th>bidQty</th><th>orderid</th><th>takeProfitOrder</th><th>takeProfitAmount</th></tr>'

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
            <td>{row['takeprofit']}</td><td>{row['updatetime']}</td><td>{row['delta']}</td><td>{askPrice}</td>\
            <td>{askQty}</td><td>{binPrice}</td><td>{bidQty}</td><td>{row['orderid']}</td><td>{row['takeProfitOrder']}</td><td>{row['takeProfitAmount']}</td></tr>"
    page += '</table>'
    page += f'<script> var myVar = setInterval(myTimer, 1000); \
        function myTimer() {{ \
            var d = new Date();\
            var t = d.toLocaleTimeString(); \
            document.getElementById("currentTime").innerHTML = t;}}\
        </script>'
    page += '</body> </html>'

    return page

#graph the current limit of a coin we have purchased
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

#graph the coins we are tracking
@app.route('/tracking', methods=['GET'])
def tracking():
    coin = request.args.get("coin")
    if coin:
        df = pd.read_csv(f'candleData/{coin}.csv', 
            encoding='utf8', 
            delimiter=',',
            names=['time', 'open', "high", "low", "close",], 
            index_col='time')
        annotations = []
        pattern = request.args.get("pattern")
        #TODO need to figure out what makes each bullish/bearish
        # add support for multiple 
        for pattern in request.args.getlist("patterns"):
            print(pattern)
            pattern_function = getattr(talib, pattern)
            results = pattern_function(df['open'], df['high'], df['low'], df['close'])
            ann = False
            df_r = results.to_frame()
            for key, value in df_r.iterrows():
                ann = False
                if int(value) != 0:
                    note = f'bullish {pattern_function.__name__}'
                    ann = True
                elif int(value) < 0:
                    note = f'bearish {pattern_function.__name__}'
                    ann = True
                # df[pattern_function.__name__] = values
                if ann:
                    annotations.append(go.layout.Annotation(x=key,
                        y=df.loc[key].at['close'],
                        font=dict(color='black'),
                        showarrow=True,
                        arrowhead=1,
                        arrowcolor="purple",
                        arrowsize=1,
                        arrowwidth=2,
                        text=note))

        layout = dict(
            title=coin,
            yaxis=go.layout.YAxis(title=go.layout.yaxis.Title( text="Price $ - US Dollars")),
            annotations=annotations
        )
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Candlestick(x=df.index, 
            open = df['open'], 
            close = df['close'], 
            low = df['low'], 
            high = df['high'],
            increasing_line_color= 'blue', decreasing_line_color= 'red'))
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_xaxes(showticklabels = False)
        plotly.offline.plot(fig, filename='templates/name.html')
        return render_template("name.html")
    files = os.listdir("candleData/")
    return render_template('tracker.html', candlestick_patterns=candlestick_patterns, coin=sorted(files))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11337, debug=True)