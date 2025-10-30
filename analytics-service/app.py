from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('analytics.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS link_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT NOT NULL,
            click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            ip_address TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Analytics database initialized!")

@app.route('/track', methods=['POST'])
def track_click():
    """Трек клика по короткой ссылке"""
    try:
        data = request.json
        short_code = data.get('short_code')
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr

        conn = sqlite3.connect('analytics.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO link_analytics (short_code, user_agent, ip_address) VALUES (?, ?, ?)',
            (short_code, user_agent, ip_address)
        )
        conn.commit()
        conn.close()

        print(f"✅ Click tracked for {short_code}")
        return jsonify({'status': 'success', 'message': 'Click tracked'})
        
    except Exception as e:
        print(f"❌ Error tracking click: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/<short_code>', methods=['GET'])
def get_analytics(short_code):
    """Получение аналитики по короткой ссылке"""
    try:
        conn = sqlite3.connect('analytics.db')
        cursor = conn.cursor()
        
        # Общее количество кликов
        cursor.execute('SELECT COUNT(*) FROM link_analytics WHERE short_code = ?', (short_code,))
        total_clicks = cursor.fetchone()[0]
        
        # Клики за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)
        cursor.execute(
            'SELECT COUNT(*) FROM link_analytics WHERE short_code = ? AND click_time > ?',
            (short_code, week_ago)
        )
        weekly_clicks = cursor.fetchone()[0]
        
        # Популярные браузеры
        cursor.execute('''
            SELECT user_agent, COUNT(*) as count 
            FROM link_analytics 
            WHERE short_code = ? 
            GROUP BY user_agent 
            ORDER BY count DESC 
            LIMIT 5
        ''', (short_code,))
        browsers = [{'browser': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'short_code': short_code,
            'total_clicks': total_clicks,
            'weekly_clicks': weekly_clicks,
            'popular_browsers': browsers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({'status': 'healthy', 'service': 'analytics-service'})

if __name__ == '__main__':
    init_db()
    print("📊 Analytics service started on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)