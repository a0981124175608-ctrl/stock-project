# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 23:24:55 2025

@author: user
"""

from flask import Blueprint, render_template
from flask_login import login_required
from models.message import Message 
from pytz import timezone
stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

@stock_bp.route('/detail/<stock_code>')
@login_required
def stock_detail(stock_code):
    # 這裡可以用 stock_code 查資料、渲染模板
    messages = Message.query.filter_by(stock_code=stock_code).order_by(Message.timestamp.asc()).all()
    taiwan = timezone('Asia/Taipei')
    for msg in messages:
       msg.local_time = msg.timestamp.astimezone(taiwan).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('stock_detail.html', stock_code=stock_code, messages=messages)
    
