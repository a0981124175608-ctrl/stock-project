# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 19:17:54 2025

@author: user
"""
from flask_wtf import FlaskForm
from flask import request ,current_app ,jsonify
from flask import Blueprint, render_template, redirect, url_for, flash,request
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_login import login_user, logout_user, login_required, current_user
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError
from utils.mail_helper import send_verification_email
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import import_string
from urllib.parse import urlparse
auth_bp = Blueprint('auth', __name__,)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('密碼', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('登入')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出')
    print("Logout success, redirecting to homepage")
    return redirect(url_for('index.home'))

# 註冊表單
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    username = StringField('Username', validators=[InputRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='密碼不一致')])
    submit = SubmitField('註冊')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此 email 已註冊')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('此使用者名稱已存在')
#驗證路由
@auth_bp.route('/verify/<token>')
def verify_email(token):
    email = User.verify_token(token)
    if not email:
        flash('驗證連結無效或已過期', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('找不到使用者', 'danger')
        return redirect(url_for('auth.register'))

    # 如果還沒驗證過，標記為驗證成功
    if not user.is_verified:
        user.is_verified = True
        db.session.commit()
        flash('帳號驗證成功，請登入', 'success')
    else:
        flash('您的帳號已經驗證過', 'info')

    return redirect(url_for('auth.login'))
    #註冊路由
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            is_verified=False
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        # 產生 token 並寄送驗證信
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(new_user.email, salt='email-confirm')
        send_verification_email(new_user.email, token)

       # flash(f"驗證信已寄出到 {new_user.email}，請查收並完成驗證", 'info')
     
        return redirect(url_for('auth.verify_notice', email=new_user.email))  
    return render_template('register.html', form=form)  
#驗證路由
@auth_bp.route('/verify_notice')
def verify_notice():
    email = request.args.get('email')
    return render_template('verify_notice.html', email=email)  
# 重寄驗證信
@auth_bp.route('/resend_verification', methods=['POST'])
def resend_verification():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if user and not user.is_verified:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(user.email, salt='email-confirm')
        send_verification_email(user.email, token)
        flash('驗證信已重新寄出，請稍後檢查您的信箱', 'info')
    return redirect(url_for('auth.verify_notice', email=email))
    #登入入游
@auth_bp.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                flash('請先完成信箱驗證')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('登入成功')
            return redirect(url_for('index.home'))
        else:
            flash('帳號或密碼錯誤')

    return render_template('login.html')
# GET 請求或登入失敗會來這裡，呈現登入頁面
    return render_template('login.html')


@auth_bp.route('/check_verification_status')
def check_verify_status():
    email = request.args.get('email')
    if not email:
        return jsonify({'verified': False})
    
    user = User.query.filter_by(email=email).first()
    if user and user.is_verified:
        return jsonify({'verified': True})
    return jsonify({'verified': False})