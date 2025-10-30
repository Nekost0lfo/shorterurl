from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

def init_db():
    """Инициализация базы данных для уведомлений"""
    try:
        conn = sqlite3.connect('notifications.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL,
                original_url TEXT NOT NULL,
                notification_type TEXT DEFAULT 'url_created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent BOOLEAN DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Notifications database initialized successfully!")
    except Exception as e:
        print(f"❌ Database error: {e}")

@app.route('/')
def index():
    """Главная страница API"""
    return jsonify({
        "message": "Notification Service API",
        "status": "working",
        "version": "1.0"
    })

@app.route('/notify', methods=['POST'])
def notify():
    """Отправка уведомления о создании новой короткой ссылки"""
    try:
        data = request.json
        short_code = data.get('short_code')
        original_url = data.get('original_url')
        notification_type = data.get('type', 'url_created')
        
        if not short_code or not original_url:
            return jsonify({'error': 'short_code and original_url are required'}), 400
        
        # Сохранение уведомления в БД
        conn = sqlite3.connect('notifications.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO notifications (short_code, original_url, notification_type) VALUES (?, ?, ?)',
            (short_code, original_url, notification_type)
        )
        conn.commit()
        conn.close()
        
        # Здесь можно добавить отправку email, SMS, webhook и т.д.
        print(f"📧 Notification sent: Short URL {short_code} created for {original_url}")
        
        return jsonify({
            'status': 'success',
            'message': 'Notification sent',
            'short_code': short_code,
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Получение списка уведомлений"""
    try:
        short_code = request.args.get('short_code')
        
        conn = sqlite3.connect('notifications.db')
        cursor = conn.cursor()
        
        if short_code:
            cursor.execute(
                'SELECT * FROM notifications WHERE short_code = ? ORDER BY created_at DESC',
                (short_code,)
            )
        else:
            cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 100')
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'short_code': row[1],
                'original_url': row[2],
                'notification_type': row[3],
                'created_at': row[4],
                'sent': bool(row[5])
            })
        
        conn.close()
        
        return jsonify({
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Проверка здоровья сервиса"""
    try:
        conn = sqlite3.connect('notifications.db')
        conn.close()
        return jsonify({
            'status': 'healthy',
            'service': 'notification-service',
            'version': '1.0'
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

if __name__ == '__main__':
    print("📧 Starting Notification Service...")
    init_db()
    print("✅ Notification service started on http://0.0.0.0:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
