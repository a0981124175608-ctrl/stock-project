# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 17:59:49 2025

@author: user
"""

# routes/index.py
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

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
@login_required
def home():
    selected_stocks = ['OTC_INDEX', '2330', '2317', '6505', '2332', '2472']

    if request.method == 'POST':
        search_code = request.form.get('search_code', '').strip()
        if search_code and search_code not in selected_stocks:
            selected_stocks.append(search_code)
        return redirect(url_for('index.home'))

    # 只傳選擇的股票給 template
    stocks_to_show = {code: STOCKS[code] for code in selected_stocks if code in STOCKS}
    return render_template('index.html', stocks=stocks_to_show)