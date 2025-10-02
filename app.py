from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import secrets
import string
from urllib.parse import urlparse

app = Flask(__name__)
DB_NAME = 'url_shortener.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            click_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    """Генерация случайного короткого кода"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_valid_url(url):
    """Проверка валидности URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Создание короткой ссылки"""
    original_url = request.json.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not is_valid_url(original_url):
        return jsonify({'error': 'Invalid URL'}), 400
    
    # Генерируем уникальный короткий код
    short_code = generate_short_code()
    while True:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
                (original_url, short_code)
            )
            conn.commit()
            break
        except sqlite3.IntegrityError:
            # Если код уже существует, генерируем новый
            short_code = generate_short_code()
        finally:
            conn.close()
    
    short_url = f"{request.host_url}{short_code}"
    return jsonify({
        'original_url': original_url,
        'short_url': short_url,
        'short_code': short_code
    })

@app.route('/<short_code>')
def redirect_to_original(short_code):
    """Перенаправление по короткой ссылке"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT original_url FROM urls WHERE short_code = ?',
        (short_code,)
    )
    result = cursor.fetchone()
    
    if result:
        # Увеличиваем счетчик кликов
        cursor.execute(
            'UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?',
            (short_code,)
        )
        conn.commit()
        conn.close()
        return redirect(result[0])
    else:
        conn.close()
        return jsonify({'error': 'Short URL not found'}), 404

@app.route('/stats/<short_code>')
def get_stats(short_code):
    """Получение статистики по короткой ссылке"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT original_url, short_code, created_at, click_count FROM urls WHERE short_code = ?',
        (short_code,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'original_url': result[0],
            'short_code': result[1],
            'created_at': result[2],
            'click_count': result[3]
        })
    else:
        return jsonify({'error': 'Short URL not found'}), 404

@app.route('/api/stats')
def get_all_stats():
    """Получение статистики всех ссылок (для администрирования)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT original_url, short_code, created_at, click_count FROM urls ORDER BY created_at DESC'
    )
    results = cursor.fetchall()
    conn.close()
    
    stats = []
    for row in results:
        stats.append({
            'original_url': row[0],
            'short_code': row[1],
            'created_at': row[2],
            'click_count': row[3],
            'short_url': f"{request.host_url}{row[1]}"
        })
    
    return jsonify(stats)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)