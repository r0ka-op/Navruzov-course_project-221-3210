## basic
from datetime import datetime

from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

## forms for auth
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

## session
from flask import session

## crypt
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasktrek.db'
app.config['SECRET_KEY'] = 'roma'

db = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # если пользователь попытается получить доступ к странице без аутентификации, то его перекинет на login


@login_manager.user_loader  # запоминает id user'а для сессии
def load_user(user_id):
    return User.query.get(int(user_id))


## classes
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)

    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")
    events = db.relationship('Event', backref='user', lazy=True, cascade="all, delete-orphan")
    settings = db.relationship('UserSettings', backref='user', lazy=True, cascade="all, delete-orphan")

    def is_active(self):
        return True

    def get_id(self):
        return str(self.user_id)


class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    priority = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50))

    __table_args__ = (
        db.CheckConstraint('priority >= 1 AND priority <= 10', name='check_priority_range'),
    )


class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime)


class UserSettings(db.Model):
    __tablename__ = 'usersettings'
    settings_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    theme = db.Column(db.String(50))


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "username"})
    first_name = StringField(validators=[InputRequired(), Length(min=2, max=30)], render_kw={"placeholder": "first_name"})
    last_name = StringField(validators=[InputRequired(), Length(min=2, max=30)], render_kw={"placeholder": "first_name"})
    email = StringField(validators=[InputRequired(), Length(min=6, max=30)], render_kw={"placeholder": "mail"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "password"})
    submit = SubmitField("Register")

    def validate_username(self, username):  # добавлен аргумент self
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('Это имя пользователя уже существует. Пожалуйста, выберите другое.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "password"})
    submit = SubmitField("Login")



## main part ------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = current_user.user_id
    tasks = Task.query.filter_by(user_id=user_id).all()
    events = Event.query.filter_by(user_id=user_id).all()
    return render_template('index.html', tasks=tasks, events=events)


@app.route('/add_to_bd', methods=['POST'])
@login_required
def add_to_database():
    title = request.form['recordTitle']
    record_type = request.form['recordType']
    date = datetime.strptime(request.form['recordDate'], '%Y-%m-%d')
    description = request.form['recordDescription']
    priority = request.form['recordPriority']
    status = 0

    if record_type == 'event':
        record = Event(user_id=current_user.user_id, title=title, description=description, event_date=date)
    elif record_type == 'task':
        record = Task(user_id=current_user.user_id, title=title, description=description, due_date=date,
                      priority=priority, status=status)
    else:
        return 'Отправленно неправильное значение'
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('index'))


# @app.route('/get_record_info/<string:record_type>/<int:record_id>', methods=['GET', 'POST'])
# @login_required
# def view_record(record_type, record_id):
#     print(record_id, record_type)
#     if record_type == 'event':
#         record = Event.query.get_or_404(record_id)
#     elif record_type == 'task':
#         record = Task.query.get_or_404(record_id)
#     else:
#         return 'Invalid record type', 400
#
#     if request.method == 'POST':
#         if 'delete' in request.form:
#             db.session.delete(record)
#             db.session.commit()
#             return redirect(url_for('index'))  # Обновите маршрут на нужный
#         else:
#             record.title = request.form['title']
#             record.description = request.form['description']
#             record_date = request.form['date']
#             record_date = datetime.strptime(record_date, '%Y-%m-%d')
#
#             if record_type == 'event':
#                 record.event_date = record_date
#             elif record_type == 'task':
#                 record.due_date = record_date
#                 record.priority = request.form['priority']
#                 record.status = request.form['status']
#
#             db.session.commit()
#             return redirect(url_for('index'))  # Обновите маршрут на нужный
#
#     return render_template('view_record.html', record=record, record_type=record_type)
#


@app.route('/get_record_info/<string:record_type>/<int:record_id>', methods=['GET', 'POST'])
@login_required
def get_record(record_id, record_type):
    print("get", record_type, record_id)
    if record_type == 'event':
        record = Event.query.get(record_id)
    elif record_type == 'task':
        record = Task.query.get(record_id)
    else:
        return jsonify({'error': 'Invalid record type'}), 400

    if record is None:
        return jsonify({'error': 'Record not found'}), 404

    if record_type == 'event':
        return jsonify({
            'type': record_type,
            'id': record.event_id,
            'title': record.title,
            'description': record.description,
            'date': record.event_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    elif record_type == 'task':
        return jsonify({
            'type': record_type,
            'id': record.task_id,
            'title': record.title,
            'description': record.description,
            'date': record.due_date.strftime('%Y-%m-%d'),
            'priority': record.priority,
            'status': record.status
        })


@app.route('/delete_record/<string:record_type>/<int:record_id>', methods=['DELETE'])
def delete_record(record_type, record_id):
    print("delete", record_type, record_id)
    if record_type == 'event':
        record = Event.query.get(record_id)
    elif record_type == 'task':
        record = Task.query.get(record_id)
    else:
        return jsonify({'error': 'Invalid record type'}), 400

    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@app.route('/update_record/<string:record_type>/<int:record_id>', methods=['PUT'])
def update_record(record_type, record_id):
    print("update", record_type, record_id)
    data = request.get_json()
    print(data)
    if record_type == 'task':
        record = Task.query.get_or_404(record_id)
        print(record)
        record.date = data.get('date', record.due_date)
        record.priority = data.get('priority', record.priority)
        record.status = data.get('status', record.status)
    elif record_type == 'event':
        record = Event.query.get_or_404(record_id)
        record.date = data.get('date', record.event_date)
    else:
        return jsonify({'success': False, 'message': 'Неверный тип записи'}), 400

    record.title = data.get('title', record.title)
    record.description = data.get('description', record.description)

    db.session.commit()
    return jsonify({'success': True})


@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            user.last_login = datetime.now()
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')

    return render_template('login.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():


    # TODO Здесь будет логика для обработки восстановления пароля


    return render_template('forgot_password.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# db.drop_all()
# db.create_all()
#
# user1 = User(username='ivan', first_name='Иван', last_name='Иванов', email='ivan@example.com', password='$2b$12$XNLQZw4Z8O0Urp0TfOTpy.JsNL4NDmFqy2mQRIJAcPT0nxnxGKIj6')
# user2 = User(username='anna', first_name='Анна', last_name='Смирнова', email='anna@example.com', password='$2b$12$8N/A6mEXnFKd3saW5CjmQeZoq/bQjdKSeKazyaXxdvCz2Z4YqEbIO')
# db.session.add_all([user1, user2])
# db.session.commit()
#
# tasks = [
#     Task(user_id=user1.user_id, title='Название задачи 1', description='Описание задачи 1',
#          due_date=datetime(2024, 6, 1), priority=5, status='В процессе'),
#     Task(user_id=user1.user_id, title='Название задачи 2', description='Описание задачи 2',
#          due_date=datetime(2024, 6, 2), priority=3, status='Завершено'),
#     Task(user_id=user1.user_id, title='Название задачи 3', description='Описание задачи 3',
#          due_date=datetime(2024, 6, 3), priority=7, status='В процессе'),
#     Task(user_id=user2.user_id, title='Название задачи 4', description='Описание задачи 4',
#          due_date=datetime(2024, 6, 4), priority=2, status='Ожидание'),
#     Task(user_id=user2.user_id, title='Название задачи 5', description='Описание задачи 5',
#          due_date=datetime(2024, 6, 5), priority=8, status='В процессе')
# ]
# db.session.add_all(tasks)
# db.session.commit()
#
# events = [
#     Event(user_id=user1.user_id, title='Название события 1', description='Описание события 1',
#           event_date=datetime(2024, 7, 1, 10, 0)),
#     Event(user_id=user1.user_id, title='Название события 2', description='Описание события 2',
#           event_date=datetime(2024, 7, 2, 11, 0)),
#     Event(user_id=user1.user_id, title='Название события 3', description='Описание события 3',
#           event_date=datetime(2024, 7, 3, 12, 0)),
#     Event(user_id=user2.user_id, title='Название события 4', description='Описание события 4',
#           event_date=datetime(2024, 7, 4, 13, 0)),
#     Event(user_id=user2.user_id, title='Название события 5', description='Описание события 5',
#           event_date=datetime(2024, 7, 5, 14, 0))
# ]
# db.session.add_all(events)
# db.session.commit()
#
# settings = [
#     UserSettings(user_id=user1.user_id, theme='Тема светлая'),
#     UserSettings(user_id=user2.user_id, theme='Тема темная')
# ]
# db.session.add_all(settings)
# db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)