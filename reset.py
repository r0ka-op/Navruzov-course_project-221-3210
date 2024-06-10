from datetime import datetime


def reset_bd(db, User, Task, Event, UserSettings):
    db.drop_all()
    db.create_all()

    user1 = User(username='ivan', first_name='Иван', last_name='Иванов', email='ivan@example.com',
                 password='$2b$12$SOi2vmahdQ7r2HocuNQbpO1IYBYvUhCWdR5KReErrh9cIkKRGcd4W')
    user2 = User(username='anna', first_name='Анна', last_name='Смирнова', email='anna@example.com',
                 password='$2b$12$SOi2vmahdQ7r2HocuNQbpO1IYBYvUhCWdR5KReErrh9cIkKRGcd4W')
    db.session.add_all([user1, user2])
    db.session.commit()

    tasks = [
        Task(user_id=user1.user_id, title='Название задачи 1', description='Описание задачи 1',
             due_date=datetime(2024, 6, 1), priority=5, status='В процессе'),
        Task(user_id=user1.user_id, title='Название задачи 2', description='Описание задачи 2',
             due_date=datetime(2024, 6, 2), priority=3, status='Завершено'),
        Task(user_id=user1.user_id, title='Название задачи 3', description='Описание задачи 3',
             due_date=datetime(2024, 6, 3), priority=7, status='В процессе'),
        Task(user_id=user2.user_id, title='Название задачи 4', description='Описание задачи 4',
             due_date=datetime(2024, 6, 4), priority=2, status='Ожидание'),
        Task(user_id=user2.user_id, title='Название задачи 5', description='Описание задачи 5',
             due_date=datetime(2024, 6, 5), priority=8, status='В процессе')
    ]
    db.session.add_all(tasks)
    db.session.commit()

    events = [
        Event(user_id=user1.user_id, title='Название события 1', description='Описание события 1',
              event_date=datetime(2024, 7, 1, 10, 0)),
        Event(user_id=user1.user_id, title='Название события 2', description='Описание события 2',
              event_date=datetime(2024, 7, 2, 11, 0)),
        Event(user_id=user1.user_id, title='Название события 3', description='Описание события 3',
              event_date=datetime(2024, 7, 3, 12, 0)),
        Event(user_id=user2.user_id, title='Название события 4', description='Описание события 4',
              event_date=datetime(2024, 7, 4, 13, 0)),
        Event(user_id=user2.user_id, title='Название события 5', description='Описание события 5',
              event_date=datetime(2024, 7, 5, 14, 0))
    ]
    db.session.add_all(events)
    db.session.commit()

    settings = [
        UserSettings(user_id=user1.user_id, theme='Тема светлая'),
        UserSettings(user_id=user2.user_id, theme='Тема темная')
    ]
    db.session.add_all(settings)
    db.session.commit()
