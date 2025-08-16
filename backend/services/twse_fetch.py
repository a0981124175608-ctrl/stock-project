# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 18:46:50 2025

@author: user
"""

# backend/services/twse_fetch.py
import requests

TWSE_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{}_tw"

def get_stock_info(stock_code):
    """
    取得即時股價資料，返回 dict。
    """
    try:
        res = requests.get(TWSE_URL.format(stock_code))
        data = res.json()
        if data.get("msgArray"):
            return data["msgArray"][0]  # 回傳單一股票資料
        else:
            return {"error": "找不到該股票代號"}
    except Exception as e:
        return {"error": str(e)}