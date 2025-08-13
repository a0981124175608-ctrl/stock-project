# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 23:30:05 2025

@author: user
"""

# models/user.py

from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # 信箱是否已驗證

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def generate_token(self):
       s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
       return s.dumps(self.email, salt='email-confirm')

    @staticmethod
    def verify_token(token, max_age=3600):
       s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
       try:
           email = s.loads(token, salt='email-confirm', max_age=max_age)
           return email
       except Exception:
           return None