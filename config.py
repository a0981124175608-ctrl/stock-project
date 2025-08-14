# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 23:17:13 2025

@author: user
"""

import os
from dotenv import load_dotenv
#指定路徑寫法
dotenv_path = r'C:/Users/user/OneDrive/Desktop/股票專題/backend/.env'
load_dotenv(dotenv_path)  # 讀取指定路徑的 .env
#不指定寫法
#load_dotenv()
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    DOMAIN = 'http://127.0.0.1:5000'
print(os.getenv("SECRET_KEY"))