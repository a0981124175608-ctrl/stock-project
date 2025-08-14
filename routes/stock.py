# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 23:24:55 2025

@author: user
"""

from flask import Blueprint, render_template,request, jsonify
from flask_login import login_required , current_user
from models.message import Message 
from pytz import timezone
from models.user import Favorite
from extensions import db, socketio

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

@stock_bp.route('/detail/<stock_code>')
@login_required
def stock_detail(stock_code):
    # 這裡可以用 stock_code 查資料、渲染模板
    messages = Message.query.filter_by(stock_code=stock_code).order_by(Message.timestamp.asc()).all()
    taiwan = timezone('Asia/Taipei')
    for msg in messages:
       msg.local_time = msg.timestamp.astimezone(taiwan).strftime('%Y-%m-%d %H:%M:%S')
 # 取得使用者最愛股票
    user_favorites = [fav.stock_code for fav in current_user.favorites]
    return render_template('stock_detail.html', 
                           stock_code=stock_code, 
                           messages=messages,
                           user_favorites=user_favorites)

@stock_bp.route('/favorite/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    data = request.get_json()
    stock_code = data.get('stock_code')
    if not stock_code:
        return jsonify({'success': False, 'message': '缺少股票代碼'}), 400

    fav = Favorite.query.filter_by(user_id=current_user.id, stock_code=stock_code).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        favorited = False
    else:
        new_fav = Favorite(user_id=current_user.id, stock_code=stock_code)
        db.session.add(new_fav)
        db.session.commit()
        favorited = True

    # 可以用 socketio 發送給前端即時更新（選擇性）
    socketio.emit('favorite_update', {
        'stock_code': stock_code,
        'favorited': favorited,
        'user': current_user.username
    }, room=f'user_{current_user.id}')

    return jsonify({'success': True, 'favorited': favorited})
    
