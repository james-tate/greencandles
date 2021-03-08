#!/usr/bin/python3

import time
import talib
import pandas as pd
import greenCandles as candles
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from greenCandles import candlestick_patterns, us_coins

#TODO add this as a input
candleInterval = '15m'
#add coins to monitor here
coins = us_coins
sockets = []


candles = candles.BinaceConnector()
coinFrames = {}

def logit(message, destination):
    with open(f"logdata/{destination}.txt", "a") as f:
        f.write(message)
        f.write("\n")

def openCSV(file):
	return pd.read_csv(file ,encoding='utf8', delimiter=',', names=['time', 'open', "high", "low", "close",], index_col='time')

def writeCSV(file, df):
	df.to_csv(file, index=True, header=False)

def process_message(msg):
	pass

def process_multi_message(msg):
	global coinFrames
	candle = msg['data']['k']
	is_candle_closed = candle['x']

	if is_candle_closed:
		coin = candle['s']
		dataFile = f'candleData/{coin}.csv'
		op = float(candle['o'])
		h = float(candle['h'])
		l = float(candle['l'])
		cl = float(candle['c'])
		df = openCSV(dataFile)

		time = datetime.fromtimestamp( (int(candle['T']) + 1)/ 1000).strftime("%H:%M:%S")
		df.loc[str(candle['T'])] = [op, h, l, cl]

		writeCSV(dataFile, df)

		annotations = []
		for pattern in candlestick_patterns:
			annotations = []
			pattern_function = getattr(talib, pattern)
			results = pattern_function(df['open'], df['high'], df['low'], df['close'])
			last = results.tail(1).values[0]
			if last != 0:
				logit(f'at {time}, pattern {pattern} is value {last} for coin {coin}', 'log')
			# ann = False
			# df_r = results.to_frame()
			# #TODO make each one of these save to a column in the df, then to the CSV,
			# # the webhook interface will create the chart when the user request
			# # but also have the monitor, or another monitor that is watching the 
			# for key, value in df_r.iterrows():
			# 	ann = False
			# 	if int(value) > 0:
			# 		note = f'bullish {pattern_function.__name__}'
			# 		ann = True
			# 	elif int(value) < 0:
			# 		note = f'bearish {pattern_function.__name__}'
			# 		ann = True
			# 	# df[pattern_function.__name__] = values
			# 	if ann:
			# 		annotations.append(go.layout.Annotation(x=key,
			# 			y=df.loc[key].at['close'],
			# 			showarrow=True,
			# 			arrowhead=1,
			# 			arrowcolor="purple",
			# 			arrowsize=2,
			# 			arrowwidth=2,
			# 			text=note))

			# if len(annotations) > 0:
			# 	layout = dict(
			#         title=candle['s'],
			#         # xaxis=go.layout.XAxis(title=go.layout.xaxis.Title( text="Time (EST - New York)"), rangeslider=dict (visible = False)),
			#         yaxis=go.layout.YAxis(title=go.layout.yaxis.Title( text="Price $ - US Dollars")),
			#         annotations=annotations
			# 	)
			# 	fig = go.Figure(layout=layout)
			# 	fig.add_trace(go.Candlestick(x=df.index, 
			# 		open = df['open'], 
			# 		close = df['close'], 
			# 		low = df['low'], 
			# 		high = df['high'],
			# 		increasing_line_color= 'blue', decreasing_line_color= 'red'))
			# 	fig.update_layout(xaxis_rangeslider_visible=False)
			# 	fig.update_xaxes(showticklabels = False)
			# 	fig.show()


def process_depth(depth_cache):
	if depth_cache is not None:
		destination = f"{depth_cache.symbol}"
		t = int(time.time())
		message = f'{t - (t%100)},{depth_cache.get_bids()[:1]},{depth_cache.get_asks()[:1]}'.replace('[[', "")
		# message = f'{datetime.now().strftime("%d%m%H%M")},{depth_cache.get_bids()[:1]},{depth_cache.get_asks()[:1]}'.replace('[[', "")
		logit(message.replace(']]', ""), destination)
		# print(int(time.time()))


for coin in coins:
	print(coin)
	pastTrades =  candles.getHistoryCandles(coin, interval=candleInterval)
	df = pd.DataFrame(columns = ["open", "high", "low", "close"])
	for x in (pastTrades):
		candle = [float(x[1]), float(x[2]), float(x[3]), float(x[4])]
		time = datetime.fromtimestamp( (int(x[0]))/ 1000).strftime("%d%m%H%M%S")
		df.loc[str(x[0])] = candle
	coinFrames[coin] = df
	writeCSV(f'candleData/{coin}.csv', df)

for coin in coins:
	sockets.append(candles.setupCandleSocket(coin, process_message, interval=candleInterval))

socketClient = candles.setupSocketMultiPlex(sockets, process_multi_message)
socketClient.start()


# 	with open(f"testData/tracker.txt", "a") as f:
# 		f.write(coin + "USDT")
# 		f.write("\n")
# streams = candles.setupDepthForSymbolsUSDT(coins, process_depth)

