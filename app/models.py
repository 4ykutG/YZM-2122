from . import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    QuizWordCount = db.Column(db.Integer, default=10)
    last_exam_date = db.Column(db.DateTime, default=None)

class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), nullable=False)
    meaning = db.Column(db.String(128), nullable=False)
    image_filename = db.Column(db.String(128))  # resim adı
    example1 = db.Column(db.String(256))
    example2 = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_global = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(64))


class UserWordProgress(db.Model):
    __tablename__ = 'user_word_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))

    correct_streak = db.Column(db.Integer, default=0)           # art arda doğru sayısı
    last_correct_date = db.Column(db.DateTime)                  # en son doğru bildiği tarih
    next_due_date = db.Column(db.DateTime)                      # tekrar zamanı
    is_completed = db.Column(db.Boolean, default=False)         # ezber tamamlandı mı



from datetime import datetime

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

