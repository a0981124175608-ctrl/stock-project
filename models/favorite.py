# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 23:26:20 2025

@author: user
"""

from extensions import db


class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_code = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Favorite user_id={self.user_id} stock_code={self.stock_code}>'