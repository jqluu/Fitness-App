from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, UserInfo
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['Get', 'Post'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # search for existing acc
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in.', category='success')
                # login 
                login_user(user, remember=True)


                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['Get', 'Post'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # search for existing acc
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        else:
            # adding new user to db
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

            # default user info
            default_user_info = UserInfo(name='John Doe', bio='Please set up your profile', age=25, gender='Male', height=67, weightGoal='Maintain', weeklyGoal = 3)

            new_user.user_info = default_user_info

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created.', category='success')
            return redirect(url_for('views.home'))


    return render_template("sign_up.html", user=current_user)

