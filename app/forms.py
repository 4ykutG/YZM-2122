from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from wtforms import IntegerField
from wtforms.validators import NumberRange

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class WordForm(FlaskForm):
    word = StringField('İngilizce Kelime', validators=[DataRequired()])
    meaning = StringField('Türkçe Anlamı', validators=[DataRequired()])
    image = FileField('Görsel (isteğe bağlı)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    example1 = StringField('Örnek Cümle 1', validators=[DataRequired()])
    example2 = StringField('Örnek Cümle 2', validators=[DataRequired()])
    category = StringField('Kategori')
    submit = SubmitField('Kelimeyi Ekle')


class SettingsForm(FlaskForm):
    quiz_count = IntegerField("Günlük Soru Sayısı", validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField("Kaydet")
