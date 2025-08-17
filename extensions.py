# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 19:00:05 2025

@author: user
"""

# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")
