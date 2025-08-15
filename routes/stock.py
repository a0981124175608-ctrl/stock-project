# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 23:24:55 2025

@author: user
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.message import Message
from models.favorite import Favorite
from extensions import db
from pytz import timezone

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

# 股票詳細頁
@stock_bp.route('/detail/<stock_code>')
@login_required
def stock_detail(stock_code):
    messages = Message.query.filter_by(stock_code=stock_code).order_by(Message.timestamp.asc()).all()

    taiwan = timezone('Asia/Taipei')
    for msg in messages:
        msg.local_time = msg.timestamp.astimezone(taiwan).strftime('%Y-%m-%d %H:%M:%S')

    # 取得使用者收藏
    user_favorites = [fav.stock_code for fav in current_user.favorites]

    return render_template('stock_detail.html',
                           stock_code=stock_code,
                           messages=messages,
                           user_favorites=user_favorites)

# 收藏/取消收藏
@stock_bp.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    stock_code = request.json.get('stock_code')
    if not stock_code:
        return jsonify({'status': 'error', 'message': '缺少股票代碼'}), 400

    fav = Favorite.query.filter_by(user_id=current_user.id, stock_code=stock_code).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        new_fav = Favorite(user_id=current_user.id, stock_code=stock_code)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'status': 'added'})
    
@stock_bp.route('/my_favorites')
@login_required
def my_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('my_favorites.html', favorites=favorites)
    