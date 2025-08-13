# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 18:42:41 2025

@author: user
"""

from extensions import db
from datetime import datetime
from models.user import User
from pytz import timezone

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    stock_code = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='messages')
    