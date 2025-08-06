from flask import Blueprint, render_template, redirect, url_for, flash, session, request, make_response, jsonify
from flask_jwt_extended import create_access_token
from flask_login import login_user, current_user, logout_user, login_required
from .models import User
from .forms import RegistrationForm, LoginForm
from . import db
import logging

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        logging.info(f'New user registered: {user.username}')
        flash('Registration successful!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['username'] = user.username
            response = make_response(redirect(url_for('main.profile')))
            response.set_cookie('welcome_name', user.username, max_age=3600)
            logging.info(f'Login successful: {user.username}')
            return response
        else:
            logging.warning(f'Failed login attempt for username: {form.username.data}')
            flash('Login failed.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logging.info(f'Logout: {current_user.username}')
    logout_user()
    session.pop('username', None)
    return redirect(url_for('main.home'))

@main.route('/profile')
@login_required
def profile():
    name = request.cookies.get('welcome_name')
    return render_template('profile.html', name=name)

@main.route('/token', methods=['GET', 'POST'])
def create_token():
    user = current_user
    if user.is_authenticated:
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token), 200
    return jsonify(error="Unauthorized"), 401