# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 17:48:57 2025

@author: user
"""

# backend/services/twse_fetch.py
from flask import Flask
from dotenv import load_dotenv
from flask_migrate import Migrate

from extensions import db, mail, login_manager, socketio
from config import Config

# Blueprints
from routes.auth import auth_bp
from routes.index import index_bp
from routes.member import member_bp
from routes.stock import stock_bp   # 這個 blueprint 內已有 url_prefix="/stock"
from routes.board import board_bp
from models.user import User

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化擴充套件
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")  # ⭐ 必須初始化 socketio

    # 資料庫遷移
    Migrate(app, db)

    # 登入設定
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 註冊藍圖（不要對 stock_bp 再加 url_prefix，避免 /stock/stock）
    app.register_blueprint(auth_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(stock_bp)   # ← 保持這樣
    app.register_blueprint(board_bp)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # ⭐ 用 socketio.run() 啟動，WebSocket 才會運作
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)