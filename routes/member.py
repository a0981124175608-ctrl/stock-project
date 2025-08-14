# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 22:52:27 2025

@author: user
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

member_bp = Blueprint('member', __name__)

@member_bp.route('/member')
@login_required
def member_center():
    return render_template('member.html', user=current_user)