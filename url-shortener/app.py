from flask import Flask, request, jsonify, render_template, redirect
import sqlite3
import os
import string
import random
import requests

app = Flask(__name__)

ANALYTICS_SERVICE_URL = os.getenv('ANALYTICS_SERVICE_URL', 'http://analytics-service:5001')
NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://notification-service:5002')

def init_db():
    """Инициализация базы данных"""
    try:
        conn = sqlite3.connect('url_shortener.db')
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
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database error: {e}")

def generate_short_code(length=6):
    """Генерация короткого кода"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Создание короткой ссылки"""
    try:
        data = request.json
        original_url = data.get('url')
        
        if not original_url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'https://' + original_url
        
        # Генерация уникального короткого кода
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        while True:
            short_code = generate_short_code()
            cursor.execute('SELECT id FROM urls WHERE short_code = ?', (short_code,))
            if not cursor.fetchone():
                break
        
        # Сохранение в БД
        cursor.execute(
            'INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
            (original_url, short_code)
        )
        conn.commit()
        conn.close()
        
        # Отправка уведомления (асинхронно, не ждем ответа)
        try:
            requests.post(
                f"{NOTIFICATION_SERVICE_URL}/notify",
                json={'short_code': short_code, 'original_url': original_url},
                timeout=1
            )
        except:
            pass  # Не критично если уведомление не отправилось
        
        base_url = request.host_url.rstrip('/')
        short_url = f"{base_url}/{short_code}"
        
        return jsonify({
            'short_code': short_code,
            'short_url': short_url,
            'original_url': original_url
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Редирект по короткому коду"""
    try:
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT original_url FROM urls WHERE short_code = ?',
            (short_code,)
        )
        result = cursor.fetchone()
        
        if result:
            original_url = result[0]
            # Увеличение счетчика кликов
            cursor.execute(
                'UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?',
                (short_code,)
            )
            conn.commit()
            conn.close()
            
            # Отправка аналитики
            try:
                requests.post(
                    f"{ANALYTICS_SERVICE_URL}/track",
                    json={'short_code': short_code},
                    headers={'User-Agent': request.headers.get('User-Agent', '')},
                    timeout=1
                )
            except:
                pass
            
            return redirect(original_url)
        else:
            conn.close()
            return jsonify({'error': 'Short URL not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats/<short_code>')
def get_stats(short_code):
    """Получение статистики по короткой ссылке"""
    try:
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT original_url, click_count, created_at FROM urls WHERE short_code = ?',
            (short_code,)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Short URL not found'}), 404
        
        original_url, click_count, created_at = result
        conn.close()
        
        # Получение расширенной аналитики
        analytics_data = {}
        try:
            response = requests.get(
                f"{ANALYTICS_SERVICE_URL}/analytics/{short_code}",
                timeout=2
            )
            if response.status_code == 200:
                analytics_data = response.json()
        except:
            pass
        
        return jsonify({
            'short_code': short_code,
            'original_url': original_url,
            'click_count': click_count,
            'created_at': created_at,
            'analytics': analytics_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Проверка соединения с БД
        conn = sqlite3.connect('url_shortener.db')
        conn.close()
        
        # Проверка других сервисов
        main_service = 'healthy'
        analytics_service = 'unknown'
        notification_service = 'unknown'
        
        try:
            response = requests.get(f"{ANALYTICS_SERVICE_URL}/health", timeout=1)
            if response.status_code == 200:
                analytics_service = 'healthy'
        except:
            analytics_service = 'unhealthy'
        
        try:
            response = requests.get(f"{NOTIFICATION_SERVICE_URL}/health", timeout=1)
            if response.status_code == 200:
                notification_service = 'healthy'
        except:
            notification_service = 'unhealthy'
        
        return jsonify({
            'status': 'healthy',
            'service': 'url-shortener',
            'version': '1.0',
            'main_service': main_service,
            'analytics_service': analytics_service,
            'notification_service': notification_service
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

if __name__ == '__main__':
    print("🚀 Starting URL Shortener...")
    init_db()
    print("✅ Services initialized, starting Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)

