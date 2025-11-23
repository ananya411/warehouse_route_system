from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash
import json

auth_bp = Blueprint('auth', __name__)  # ✅ THIS must exist

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with open('data/users.json') as f:
            users = json.load(f)
        
        for user in users:
            if user['username'] == username and check_password_hash(user['password'], password):
                session['user'] = username
                session['role'] = user['role']
                return redirect('/dashboard')
        
        flash("Invalid credentials", "danger")
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
