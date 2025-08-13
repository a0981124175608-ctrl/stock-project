# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 11:50:34 2025

@author: user
"""

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.message import Message  # 假設你有這個留言模型
from flask import jsonify
from datetime import datetime
from pytz import timezone

board_bp = Blueprint('board', __name__)


@board_bp.route('/post/<stock_code>', methods=['POST'])
@login_required
def post_message(stock_code):
    content = request.form.get('message', '').strip()
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, error='留言不能為空白')
        else:
            flash("留言不能為空白")
            return redirect(url_for('stock.stock_detail', stock_code=stock_code))

    message = Message(
        user_id=current_user.id,
        stock_code=stock_code,
        content=content,
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()

    # 判斷是否 AJAX 請求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        taipei = timezone('Asia/Taipei')
        local_time = message.timestamp.replace(tzinfo=timezone('UTC')).astimezone(taipei).strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(success=True,
                       username=current_user.username,
                       content=content,
                       local_time=local_time)

    flash("留言已送出！")
    return redirect(url_for('stock.stock_detail', stock_code=stock_code))