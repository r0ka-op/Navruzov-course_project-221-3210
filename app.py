import csv
import io
from datetime import datetime, timedelta
from babel.dates import format_datetime
import pandas as pd

from flask import Flask, render_template, url_for, redirect, request, jsonify, flash,  send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, ValidationError

from flask_bcrypt import Bcrypt

from reset import reset_bd

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasktrek.db'
app.config['SECRET_KEY'] = 'roma'

db = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def format_date(value):
    return format_datetime(value, "EEEE dd-MM-yyyy", locale='ru_RU')
app.jinja_env.filters['format_date'] = format_date


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


class ImportForm(FlaskForm):
    csv_file = FileField('CSV файл', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Только CSV файлы!')
    ])



@app.route('/reset_bd')
@login_required
def reset():
    return reset_bd(db, User, Task, Event, UserSettings)



@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = current_user.user_id
    tasks = Task.query.filter_by(user_id=user_id).all()
    events = Event.query.filter_by(user_id=user_id).all()
    form = ImportForm()
    return render_template('index.html', tasks=tasks, events=events, form=form)


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


@app.route('/export_csv', methods=['GET'])
@login_required
def export_csv():
    user_id = current_user.user_id
    tasks = Task.query.filter_by(user_id=user_id).all()
    events = Event.query.filter_by(user_id=user_id).all()

    print(f"Tasks: {tasks}")
    print(f"Events: {events}")

    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['Task ID', 'Title', 'Description', 'Due Date', 'Priority', 'Status'])
    for task in tasks:
        writer.writerow([task.task_id, task.title, task.description, task.due_date, task.priority, task.status])

    writer.writerow([])

    writer.writerow(['Event ID', 'Title', 'Description', 'Event Date'])
    for event in events:
        writer.writerow([event.event_id, event.title, event.description, event.event_date])

    csv_data = output.getvalue().encode('utf-8')
    byte_output = io.BytesIO(csv_data)
    byte_output.seek(0)

    return send_file(byte_output, mimetype='text/csv', as_attachment=True, download_name='data_export.csv')


@app.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    form = ImportForm()

    if form.validate_on_submit():
        csv_file = form.csv_file.data
        if csv_file.filename.endswith('.csv'):
            try:
                lines = csv_file.read().decode('utf-8').splitlines()

                task_start_idx = None
                event_start_idx = None

                for idx, line in enumerate(lines):
                    if line.startswith('Task ID'):
                        task_start_idx = idx
                    elif line.startswith('Event ID'):
                        event_start_idx = idx

                if task_start_idx is None or event_start_idx is None:
                    flash('CSV файл должен содержать обе секции: Task и Event', 'danger')
                    return redirect(url_for('index'))

                tasks_lines = lines[task_start_idx:event_start_idx]
                events_lines = lines[event_start_idx:]

                tasks_df = pd.read_csv(io.StringIO('\n'.join(tasks_lines)))
                events_df = pd.read_csv(io.StringIO('\n'.join(events_lines)))

                if 'Due Date' not in tasks_df.columns:
                    flash("CSV файл должен содержать колонку 'Due Date' в секции Task", 'danger')
                    return redirect(url_for('index'))

                if 'Event Date' not in events_df.columns:
                    flash("CSV файл должен содержать колонку 'Event Date' в секции Event", 'danger')
                    return redirect(url_for('index'))

                tasks_df['Due Date'] = pd.to_datetime(tasks_df['Due Date'], errors='coerce')
                events_df['Event Date'] = pd.to_datetime(events_df['Event Date'], errors='coerce')

                for index, row in tasks_df.iterrows():
                    new_task = Task(
                        user_id=current_user.user_id,
                        title=row['Title'],
                        description=row['Description'],
                        due_date=row['Due Date'].date() if not pd.isnull(row['Due Date']) else None,
                        priority=row['Priority'],
                        status=row['Status']
                    )
                    db.session.add(new_task)

                for index, row in events_df.iterrows():
                    new_event = Event(
                        user_id=current_user.user_id,
                        title=row['Title'],
                        description=row['Description'],
                        event_date=row['Event Date'] if not pd.isnull(row['Event Date']) else None
                    )
                    db.session.add(new_event)

                db.session.commit()
                flash('CSV файл успешно импортирован!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при импорте CSV файла: {str(e)}', 'danger')
                return redirect(url_for('index'))
        else:
            flash('Файл должен быть формата CSV (.csv)', 'danger')
            return redirect(url_for('index'))

    return render_template('import_csv.html', form=form)


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    query = request.form.get('query')
    print(query)
    user_id = current_user.user_id

    if not query:
        return jsonify({'tasks': [], 'events': []})

    tasks = Task.query.filter(Task.user_id == user_id, Task.title.ilike(f'%{query}%')).all()
    events = Event.query.filter(Event.user_id == user_id, Event.title.ilike(f'%{query}%')).all()

    tasks_data = [{'task_id': task.task_id, 'title': task.title, 'due_date': task.due_date, 'description': task.description} for task in tasks]
    print(tasks_data)
    events_data = [{'event_id': event.event_id, 'title': event.title} for event in events]
    print(events_data)

    return jsonify({'tasks': tasks_data, 'events': events_data})


@app.route('/search_by_date', methods=['POST', 'GET'])
@login_required
def search_by_date():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    print(start_date, end_date)
    print(request.data)
    user_id = current_user.user_id

    if not start_date or not end_date:
        return jsonify({'error': 'Необходимо указать обе даты'})

    try:
        print(1)
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date = start_date - timedelta(days=1)
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Некорректный формат даты'})

    print(start_date, end_date)
    tasks = Task.query.filter(Task.user_id == user_id, Task.due_date.between(start_date, end_date)).all()
    events = Event.query.filter(Event.user_id == user_id, Event.event_date.between(start_date, end_date)).all()
    print(tasks, events)
    tasks_data = [{'task_id': task.task_id, 'title': task.title, 'due_date': task.due_date.strftime('%m-%d-%Y'), 'description': task.description} for task in tasks]
    events_data = [{'event_id': event.event_id, 'title': event.title, 'event_date': event.event_date.strftime('%d-%m-%Y')} for event in events]

    return jsonify({'tasks': tasks_data, 'events': events_data})


if __name__ == '__main__':
    app.run(debug=True)