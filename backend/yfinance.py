# -*- coding: utf-8 -*-
"""
Created on Sat Aug 16 20:33:58 2025

@author: user
"""

import yfinance as yf

# 抓台積電 2330.TW
stock = yf.Ticker("2330.TW")

# 取得最近 60 天的日線 OHLC 資料
df = stock.history(period="1d", interval="1d")

print(df.head())