# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 17:48:57 2025

@author: user
"""

# backend/services/twse_fetch.py
import traceback
# import pretttable
from flask import Flask
from extensions import db, mail, login_manager
from routes.auth import auth_bp
from models.user import User
from dotenv import load_dotenv
from routes.index import index_bp
from routes.member import member_bp
from config import Config
from routes.stock import stock_bp
from routes.board import board_bp
from flask_migrate import Migrate
 
load_dotenv()  # 讀取 .env 檔案

def create_app():
    app=Flask(__name__)
    # 設定（暫時簡化，之後可拆成 config.py）
    app.config.from_object(Config)
    migrate = Migrate(app, db) 
    
    # 初始化擴充套件
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 設定登入路由（未登入會自動轉跳這個）
    login_manager.login_view = 'auth.login'

    # 綁定 user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 註冊藍圖
    app.register_blueprint(auth_bp,)
    app.register_blueprint(member_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(board_bp)
    
  

    return app
# 執行進入點
if __name__ == '__main__':
    try:
        app = create_app()
        print("✅ App created successfully")
        with app.app_context():
          db.create_all()
        app.run(debug=True,use_reloader=False)
    except Exception as e:
        print("❌ 啟動失敗:", e)
        