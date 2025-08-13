# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 18:48:48 2025

@author: user
"""

from extensions import db
from models.user import User
from app import create_app  # 這裡是你的 Flask app 工廠函式的檔名和函式名稱

app = create_app()
app.app_context().push()

User.query.delete()
db.session.commit()
print("會員資料已清除")