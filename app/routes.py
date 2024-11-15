from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateForm

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Введены неверные данные','danger')
    return render_template('login.html', form=form, title='Login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    change_flag = 0
    user = User.query.get(current_user.id)
    form = UpdateForm(obj=user)
    if form.validate_on_submit():
        if user.username != form.username.data:
            user_double = User.query.filter_by(username=form.username.data).first()
            if user_double:
                flash('Такое username уже существует', 'danger')
            else:
                user.username = form.username.data
                change_flag = 1
        if user.email != form.email.data:
            user_double = User.query.filter_by(email=form.email.data).first()
            if user_double:
                flash('Такая почта уже используется', 'danger')
            else:
                user.email = form.email.data
                change_flag = 1
        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            change_flag = 1

        if change_flag:
            db.session.commit()
            flash('Данные аккаунта успешно изменены!', 'success')
    return render_template('account.html', form=form, title='Update')

