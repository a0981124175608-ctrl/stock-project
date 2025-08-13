# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 17:59:49 2025

@author: user
"""

# routes/index.py
from flask import Blueprint, render_template, request, redirect, url_for

index_bp = Blueprint('index', __name__)

# 靜態股票清單（櫃買指數 + 三支自選股票）
STOCKS = {
    'OTC_INDEX': '櫃買指數',
    '2330': '台積電',
    '2317': '鴻海',
    '6505': '台塑化',
    '2332': '友訊',
    '2472': '立隆電'
    
}

@index_bp.route('/', methods=['GET', 'POST'])
def home():
    selected_stocks = ['OTC_INDEX', '2330', '2317', '6505' ,'2332' ,'2472']

    # 搜尋功能：表單送出股票代碼，跳轉頁面（這裡先跳回首頁）
    
    if request.method == 'POST':
        search_code = request.form.get('search_code', '').strip()
        if search_code and search_code not in selected_stocks:
            # 假設加入自選（這裡先不動，後續會改成動態）
            selected_stocks.append(search_code)
        return redirect(url_for('index.home'))

    return render_template('index.html', stocks=STOCKS, selected_stocks=selected_stocks)