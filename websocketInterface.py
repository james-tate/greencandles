#!/usr/bin/python3

import time
import pandas as pd
import greenCandles as candles
from datetime import datetime


candles = candles.BinaceConnector()

def logit(message, destination):
    with open(f"testData/{destination}.txt", "a") as f:
        f.write(message)
        f.write("\n")

def process_depth(depth_cache):
	if depth_cache is not None:
		destination = f"{depth_cache.symbol}"
		message = f'{datetime.now().strftime("%d_%m_%Y_%H_%M")},{depth_cache.get_bids()[:1]},{depth_cache.get_asks()[:1]}'.replace('[[', "")
		logit(message.replace(']]', ""), destination)

coins = ['LTC', 'BTC']
for coin in coins:
	with open(f"testData/tracker.txt", "a") as f:
		f.write(coin)
		f.write("\n")
streams = candles.setupDepthForSymbolsUSDT(coins, process_depth)
