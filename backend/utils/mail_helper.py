# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 23:09:22 2025

@author: user
"""

# utils/mail_helper.py
from flask_mail import Message
from flask import current_app
from extensions import mail

def send_verification_email(to_email, token):
    link = f"{current_app.config['DOMAIN']}/verify/{token}"
    msg = Message("帳號驗證", sender=current_app.config['MAIL_USERNAME'], recipients=[to_email])
    msg.body = f"歡迎註冊！請點擊下方連結驗證帳號：\n\n{link}\n\n若你未註冊，請忽略此信。"
    mail.send(msg)