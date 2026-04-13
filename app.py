import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')  # Для flash-сообщений

# Гибкое подключение к БД: SQLite по умолчанию, PostgreSQL при наличии DATABASE_URL
db_url = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    """READ: Отображение всех задач"""
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    """CREATE: Добавление новой задачи"""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    # Валидация: название обязательно
    if not title:
        flash('Название задачи обязательно!', 'error')
        return redirect(url_for('index'))
    
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()
    flash('Задача добавлена!', 'success')
    return redirect(url_for('index'))

# 🆕 НОВЫЕ МАРШРУТЫ ДЛЯ РЕДАКТИРОВАНИЯ
@app.route('/edit/<int:task_id>', methods=['GET'])
def edit_form(task_id):
    """Показывает форму редактирования задачи"""
    task = db.session.get(Task, task_id)
    if not task:
        flash('Задача не найдена!', 'error')
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit(task_id):
    """UPDATE: Обработка сохранения изменений"""
    task = db.session.get(Task, task_id)
    if not task:
        flash('Задача не найдена!', 'error')
        return redirect(url_for('index'))
    
    # Получаем и валидируем данные
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Название задачи обязательно!', 'error')
        return redirect(url_for('edit_form', task_id=task_id))
    
    # Обновляем поля
    task.title = title
    task.description = description
    db.session.commit()
    
    flash('Задача обновлена!', 'success')
    return redirect(url_for('index'))
# 🆕 КОНЕЦ НОВЫХ МАРШРУТОВ

@app.route('/toggle/<int:task_id>')
def toggle(task_id):
    """UPDATE: Переключение статуса выполнения"""
    task = db.session.get(Task, task_id)
    if task:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    """DELETE: Удаление задачи"""
    task = db.session.get(Task, task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Задача удаленаasd!', 'success')
    return redirect(url_for('index'))

@app.route('/health')
def health():
    """Healthcheck endpoint для Docker и мониторинга"""
    return {"status": "healthy", "version" : "1.2.0"}, 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # debug=False для продакшена, можно вынести в env
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')