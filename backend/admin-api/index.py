import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta


def handler(event: dict, context) -> dict:
    """API для админ-панели LeoMatch - получение статистики и управление пользователями"""
    
    method = event.get('httpMethod', 'GET')
    params = event.get('queryStringParameters', {}) or {}
    action = params.get('action', 'stats')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    try:
        conn = get_db_connection()
        
        # Получение статистики для дашборда
        if method == 'GET' and action == 'stats':
            stats = get_stats(conn)
            return response(200, stats)
        
        # Получение пользователей
        elif method == 'GET' and action == 'users':
            status = params.get('status', 'all')
            users = get_users(conn, status)
            return response(200, {'users': users})
        
        # Получение матчей
        elif method == 'GET' and action == 'matches':
            matches = get_matches(conn)
            return response(200, {'matches': matches})
        
        # Получение сообщений
        elif method == 'GET' and action == 'messages':
            match_id = params.get('match_id')
            messages = get_messages(conn, match_id)
            return response(200, {'messages': messages})
        
        # Модерация пользователя
        elif method == 'POST' and action == 'moderate':
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            mod_action = body.get('action')  # 'approve' or 'reject'
            result = moderate_user(conn, user_id, mod_action)
            return response(200, result)
        
        # Обновление статуса пользователя
        elif method == 'PUT' and action == 'update_user':
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')
            status = body.get('status')
            result = update_user_status(conn, user_id, status)
            return response(200, result)
        
        else:
            return response(404, {'error': 'Endpoint not found'})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': str(e)})
    finally:
        if 'conn' in locals():
            conn.close()


def get_db_connection():
    """Подключение к базе данных"""
    return psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=RealDictCursor
    )


def response(status_code: int, data: dict) -> dict:
    """Формирование ответа"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data, default=str),
        'isBase64Encoded': False
    }


def get_stats(conn) -> dict:
    """Получение статистики для дашборда"""
    cur = conn.cursor()
    
    # Общее количество пользователей
    cur.execute("SELECT COUNT(*) as total FROM users")
    total_users = cur.fetchone()['total']
    
    # Пользователи за неделю
    week_ago = datetime.now() - timedelta(days=7)
    cur.execute("SELECT COUNT(*) as total FROM users WHERE created_at > %s", (week_ago,))
    users_this_week = cur.fetchone()['total']
    
    # Активные матчи
    cur.execute("SELECT COUNT(*) as total FROM matches WHERE status = 'active'")
    active_matches = cur.fetchone()['total']
    
    # Матчи за неделю
    cur.execute("SELECT COUNT(*) as total FROM matches WHERE created_at > %s", (week_ago,))
    matches_this_week = cur.fetchone()['total']
    
    # Сообщения сегодня
    today = datetime.now().date()
    cur.execute("SELECT COUNT(*) as total FROM messages WHERE DATE(created_at) = %s", (today,))
    messages_today = cur.fetchone()['total']
    
    # Пользователи на модерации
    cur.execute("SELECT COUNT(*) as total FROM users WHERE status = 'pending' OR (status = 'active' AND verified = FALSE)")
    pending_moderation = cur.fetchone()['total']
    
    # Активность по дням недели (последние 7 дней)
    cur.execute("""
        SELECT 
            DATE(created_at) as day,
            COUNT(*) as matches_count
        FROM matches
        WHERE created_at > %s
        GROUP BY DATE(created_at)
        ORDER BY day
    """, (week_ago,))
    daily_matches = cur.fetchall()
    
    cur.execute("""
        SELECT 
            DATE(created_at) as day,
            COUNT(*) as messages_count
        FROM messages
        WHERE created_at > %s
        GROUP BY DATE(created_at)
        ORDER BY day
    """, (week_ago,))
    daily_messages = cur.fetchall()
    
    # Объединяем данные по дням
    days_map = {}
    for item in daily_matches:
        day_str = item['day'].strftime('%Y-%m-%d')
        days_map[day_str] = {'matches': item['matches_count'], 'messages': 0}
    
    for item in daily_messages:
        day_str = item['day'].strftime('%Y-%m-%d')
        if day_str in days_map:
            days_map[day_str]['messages'] = item['messages_count']
        else:
            days_map[day_str] = {'matches': 0, 'messages': item['messages_count']}
    
    daily_activity = [
        {'day': day, 'matches': data['matches'], 'messages': data['messages']}
        for day, data in sorted(days_map.items())
    ]
    
    cur.close()
    
    return {
        'totalUsers': total_users,
        'usersThisWeek': users_this_week,
        'usersGrowth': round((users_this_week / max(total_users - users_this_week, 1)) * 100, 1),
        'activeMatches': active_matches,
        'matchesThisWeek': matches_this_week,
        'matchesGrowth': round((matches_this_week / max(active_matches - matches_this_week, 1)) * 100, 1),
        'todayMessages': messages_today,
        'pendingModeration': pending_moderation,
        'dailyActivity': daily_activity
    }


def get_users(conn, status: str = 'all'):
    """Получение списка пользователей"""
    cur = conn.cursor()
    
    if status == 'all':
        cur.execute("""
            SELECT id, telegram_id, username, first_name, age, gender, city, bio, 
                   photo_url, status, verified, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 100
        """)
    else:
        cur.execute("""
            SELECT id, telegram_id, username, first_name, age, gender, city, bio, 
                   photo_url, status, verified, created_at
            FROM users
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT 100
        """, (status,))
    
    users = cur.fetchall()
    cur.close()
    
    return [dict(user) for user in users]


def get_matches(conn):
    """Получение списка матчей"""
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            m.id,
            m.status,
            m.created_at,
            u1.first_name as user1_name,
            u1.age as user1_age,
            u2.first_name as user2_name,
            u2.age as user2_age,
            (SELECT COUNT(*) FROM messages WHERE match_id = m.id) as message_count
        FROM matches m
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        WHERE m.status = 'active'
        ORDER BY m.created_at DESC
        LIMIT 50
    """)
    
    matches = cur.fetchall()
    cur.close()
    
    return [dict(match) for match in matches]


def get_messages(conn, match_id: str = None):
    """Получение сообщений"""
    cur = conn.cursor()
    
    if match_id:
        cur.execute("""
            SELECT 
                msg.id,
                msg.message_text,
                msg.created_at,
                u.first_name as sender_name
            FROM messages msg
            JOIN users u ON msg.sender_id = u.id
            WHERE msg.match_id = %s
            ORDER BY msg.created_at DESC
            LIMIT 100
        """, (match_id,))
    else:
        cur.execute("""
            SELECT 
                msg.id,
                msg.match_id,
                msg.message_text,
                msg.created_at,
                u.first_name as sender_name
            FROM messages msg
            JOIN users u ON msg.sender_id = u.id
            ORDER BY msg.created_at DESC
            LIMIT 100
        """)
    
    messages = cur.fetchall()
    cur.close()
    
    return [dict(msg) for msg in messages]


def moderate_user(conn, user_id: int, action: str):
    """Модерация пользователя"""
    cur = conn.cursor()
    
    if action == 'approve':
        cur.execute("""
            UPDATE users 
            SET verified = TRUE, status = 'active'
            WHERE id = %s
        """, (user_id,))
        conn.commit()
        return {'success': True, 'message': 'User approved'}
    
    elif action == 'reject':
        cur.execute("""
            UPDATE users 
            SET status = 'banned'
            WHERE id = %s
        """, (user_id,))
        conn.commit()
        return {'success': True, 'message': 'User rejected'}
    
    cur.close()
    return {'success': False, 'message': 'Invalid action'}


def update_user_status(conn, user_id: int, status: str):
    """Обновление статуса пользователя"""
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE users 
        SET status = %s
        WHERE id = %s
    """, (status, user_id))
    conn.commit()
    cur.close()
    
    return {'success': True, 'message': 'Status updated'}