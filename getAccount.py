#!/usr/bin/python3


#TODO change polling to websocket design

import time
import pandas as pd
import greenCandles as candles
import plotly
import plotly.graph_objects as go
import plotly.express as px

client = candles.BinaceConnector()

assets = client.getAssetPrices()

coin = []
price = []

for x in assets:
	if 'USD' not in x['asset']:
		coin.append(x['asset'])
		price.append(x['total'])

df = pd.DataFrame(price, index=coin)
fig = px.bar(df)
fig.show()