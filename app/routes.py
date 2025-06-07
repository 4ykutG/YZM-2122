from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from .forms import RegisterForm, LoginForm, WordForm
from . import db, login_manager
import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime
from sqlalchemy import and_
from .models import Word, UserWordProgress
from .models import Word, UserWordProgress
from datetime import datetime
from .forms import SettingsForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
            QuizWordCount=10
        )
        db.session.add(user)
        db.session.commit()




        db.session.commit()

        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Geçersiz giriş.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')



@main.route('/add-word', methods=['GET', 'POST'])
@login_required
def add_word():
    form = WordForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('app/static/uploads', filename)
            image_file.save(image_path)

        word = Word(
            word=form.word.data,
            meaning=form.meaning.data,
            image_filename=filename,
            example1=form.example1.data,
            example2=form.example2.data,
            user_id=current_user.id,
            category = form.category.data
        )
        db.session.add(word)
        db.session.commit()
        flash('Kelime başarıyla eklendi!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('add_word.html', form=form)




from flask import session
import random

@main.route('/exam')
@login_required
def exam():
    if current_user.last_exam_date and current_user.last_exam_date.date() == datetime.utcnow().date():
        flash("Bugün sınavınızı zaten tamamladınız.", "warning")
        return redirect(url_for('main.dashboard'))

    user_id = current_user.id
    max_questions = current_user.QuizWordCount or 10

    # 🔁 Tekrar zamanı gelen doğru bilinen kelimeler
    due_words_progress = UserWordProgress.query.filter(
        and_(
            UserWordProgress.user_id == user_id,
            UserWordProgress.correct_streak > 0,
            UserWordProgress.is_completed == False,
            UserWordProgress.next_due_date <= datetime.utcnow()
        )
    ).all()

    due_word_ids = [p.word_id for p in due_words_progress]
    exam_word_ids = due_word_ids.copy()
    used_word_ids = set(due_word_ids)

    # ✅ Yeni kelimeler
    known_word_ids = db.session.query(UserWordProgress.word_id).filter_by(user_id=user_id).all()
    known_word_ids = [wid for (wid,) in known_word_ids]

    new_words = Word.query.filter(
        Word.is_global == True,
        ~Word.id.in_(known_word_ids + list(used_word_ids))
    ).limit(max_questions).all()

    for word in new_words:
        exam_word_ids.append(word.id)

        progress = UserWordProgress(
            user_id=user_id,
            word_id=word.id,
            correct_streak=0,
            is_completed=False,
            next_due_date=datetime.utcnow()
        )
        db.session.add(progress)

    if not exam_word_ids:
        flash("Bugün çözülmesi gereken kelime bulunamadı.", "info")
        return redirect(url_for('main.dashboard'))

    random.shuffle(exam_word_ids)

    session['exam_words'] = exam_word_ids
    session['current_index'] = 0

    # ✅ Kullanıcının sınav tarihi güncellenir
    current_user.last_exam_date = datetime.utcnow()
    db.session.add(current_user)

    db.session.commit()

    return redirect(url_for('main.show_question'))








from flask import request
from datetime import datetime, timedelta

def get_next_due_date(streak):
    if streak == 1:
        return datetime.utcnow() + timedelta(days=1)
    elif streak == 2:
        return datetime.utcnow() + timedelta(weeks=1)
    elif streak == 3:
        return datetime.utcnow() + timedelta(days=30)
    elif streak == 4:
        return datetime.utcnow() + timedelta(days=90)
    elif streak == 5:
        return datetime.utcnow() + timedelta(days=180)
    elif streak >= 6:
        return None


from .models import Answer

@main.route('/submit-answer/<int:word_id>', methods=['POST'])
@login_required
def submit_answer(word_id):
    user_id = current_user.id
    user_input = request.form.get('answer', '').strip().lower()
    word = Word.query.get(word_id)

    if not word:
        flash('Kelime bulunamadı.', 'danger')
        return redirect(url_for('main.show_question'))

    correct_answer = word.meaning.strip().lower()

    progress = UserWordProgress.query.filter_by(user_id=user_id, word_id=word_id).first()
    if not progress:
        progress = UserWordProgress(
            user_id=user_id,
            word_id=word_id,
            correct_streak=0,
            is_completed=False,
            next_due_date=datetime.utcnow()
        )

    if user_input == correct_answer:
        progress.correct_streak += 1
        progress.last_correct_date = datetime.utcnow()
        if progress.correct_streak >= 6:
            progress.is_completed = True
            progress.next_due_date = None
            flash(f"✅ '{word.word}' kelimesini tamamen öğrendiniz!", 'success')
        else:
            progress.next_due_date = get_next_due_date(progress.correct_streak)
            flash(f"✅ Doğru! Tekrar zamanı: {progress.next_due_date.date()}", 'success')
    else:
        progress.correct_streak = 0
        progress.next_due_date = datetime.utcnow() + timedelta(days=1)
        flash(f"❌ Yanlış. Doğru cevap: {word.meaning}", 'danger')

    db.session.add(progress)

    # ✅ Kullanıcının sınav tarihini güncelle (ilk cevabıysa)
    if not current_user.last_exam_date or current_user.last_exam_date.date() < datetime.utcnow().date():
        current_user.last_exam_date = datetime.utcnow()
        db.session.add(current_user)

    # ➕ Cevap kaydını Answer tablosuna ekle
    answer = Answer(
        user_id=user_id,
        word_id=word_id,
        is_correct=(user_input == correct_answer)
    )
    db.session.add(answer)

    db.session.commit()

    # 🔄 Sonraki soruya geç
    index = session.get('current_index', 0)
    session['current_index'] = index + 1

    return redirect(url_for('main.show_question'))




from sqlalchemy import func, case

from sqlalchemy import func, case

@main.route('/report')
@login_required
def report():
    user_id = current_user.id

    # Her kategori için toplam cevap sayısı ve doğru sayısı
    category_stats = db.session.query(
        Word.category,
        func.count(Answer.id).label("answered"),
        func.sum(case((Answer.is_correct == True, 1), else_=0)).label("correct")
    ).join(Word, Answer.word_id == Word.id)\
     .filter(Answer.user_id == user_id)\
     .group_by(Word.category)\
     .all()

    report_data = []
    for category, answered, correct in category_stats:
        correct = correct or 0
        percent = int((correct / answered) * 100) if answered else 0
        report_data.append({
            "category": category or "Bilinmeyen",
            "answered": answered,
            "correct": correct,
            "percent": percent
        })

    return render_template("report.html", report_data=report_data)



from reportlab.pdfgen import canvas
from flask import make_response

@main.route('/report/download')
@login_required
def download_report():
    from sqlalchemy import func, case

    user_id = current_user.id

    category_stats = db.session.query(
        Word.category,
        func.count(UserWordProgress.id).label("total"),
        func.sum(case(
            (UserWordProgress.is_completed == True, 1),
            else_=0
        )).label("completed")
    ).join(Word, UserWordProgress.word_id == Word.id)\
     .filter(UserWordProgress.user_id == user_id)\
     .group_by(Word.category)\
     .all()

    # PDF response
    response = make_response()
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=report.pdf"

    c = canvas.Canvas(response)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Kullanıcı: {current_user.username}")
    c.setFont("Helvetica", 12)

    y = 760
    for category, total, completed in category_stats:
        percent = int((completed / total) * 100) if total else 0
        c.drawString(100, y, f"{category or 'Bilinmeyen'} → {completed}/{total} doğru ({percent}%)")
        y -= 20

    c.showPage()
    c.save()
    return response


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = current_user
    form = SettingsForm(quiz_count=user.QuizWordCount)

    if form.validate_on_submit():
        user.QuizWordCount = form.quiz_count.data
        db.session.commit()
        flash("Ayarlar başarıyla kaydedildi.", "success")
        return redirect(url_for('main.dashboard'))

    return render_template("settings.html", form=form)


@main.route('/question')
@login_required
def show_question():
    exam_words = session.get('exam_words', [])
    index = session.get('current_index', 0)

    if index >= len(exam_words):
        flash("Sınav tamamlandı!", "info")
        return redirect(url_for('main.dashboard'))

    word_id = exam_words[index]
    word = Word.query.get(word_id)

    return render_template('exam_question.html', word=word, index=index + 1, total=len(exam_words))


@main.route('/wordle/start')
@login_required
def wordle_start():
    from sqlalchemy.sql import func

    # 6 defa doğru bilinen kelimelerden rastgele birini seç
    learned_words = db.session.query(Word).join(UserWordProgress).filter(
        UserWordProgress.user_id == current_user.id,
        UserWordProgress.correct_streak >= 6
    ).order_by(func.newid()).all()

    if not learned_words:
        flash("Henüz yeterli ezberlenmiş kelimeniz yok.", "warning")
        return redirect(url_for('main.dashboard'))

    selected_word = learned_words[0].word.lower()

    session['wordle_target'] = selected_word
    session['wordle_attempts'] = []

    return redirect(url_for('main.wordle_game'))


@main.route('/wordle/game', methods=['GET', 'POST'])
@login_required
def wordle_game():
    target = session.get('wordle_target')
    attempts = session.get('wordle_attempts', [])

    if not target:
        flash("Oyun başlatılamadı. Lütfen yeniden deneyin.", "danger")
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        guess = request.form.get('guess', '').strip().lower()
        if len(guess) != len(target):
            flash(f"{len(target)} harfli bir kelime girmelisiniz.", "danger")
        else:
            # Harf kontrolü
            result = []
            for i, char in enumerate(guess):
                if char == target[i]:
                    result.append(('green', char))
                elif char in target:
                    result.append(('yellow', char))
                else:
                    result.append(('gray', char))

            attempts.append(result)
            session['wordle_attempts'] = attempts

            if guess == target:
                return redirect(url_for('main.wordle_success'))

    return render_template('wordle_game.html', target_len=len(target), attempts=attempts)


@main.route('/wordle/success')
@login_required
def wordle_success():
    return render_template("wordle_success.html")
