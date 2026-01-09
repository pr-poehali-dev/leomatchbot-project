import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests


def handler(event: dict, context) -> dict:
    """Webhook для обработки сообщений от Telegram бота LeoMatch"""
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Получаем данные из обновления Telegram
        message = body.get('message', {})
        if not message:
            # Может быть callback_query
            callback_query = body.get('callback_query', {})
            if callback_query:
                return handle_callback(callback_query)
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user_data = message.get('from', {})
        
        if not chat_id:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
        
        # Обработка команд
        if text.startswith('/start'):
            return handle_start(chat_id, user_data)
        elif text.startswith('/profile'):
            return handle_profile(chat_id, user_data)
        elif text.startswith('/search'):
            return handle_search(chat_id, user_data)
        elif text.startswith('/stop') or text == '⏸ Остановить поиск':
            return handle_stop(chat_id, user_data)
        elif text == '👤 Моя анкета':
            return handle_profile(chat_id, user_data)
        elif text == '🔍 Найти пару':
            return handle_search(chat_id, user_data)
        elif text == '⚙️ Настройки':
            return handle_settings(chat_id, user_data)
        else:
            # Обработка обычных сообщений в чате
            return handle_message(chat_id, user_data, text)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_db_connection():
    """Подключение к базе данных"""
    return psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=RealDictCursor
    )


def send_message(chat_id: int, text: str, reply_markup=None):
    """Отправка сообщения через Telegram API"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    requests.post(url, json=payload)


def handle_start(chat_id: int, user_data: dict) -> dict:
    """Обработка команды /start"""
    telegram_id = user_data.get('id')
    username = user_data.get('username', '')
    first_name = user_data.get('first_name', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем, есть ли пользователь в БД
    cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    
    if not user:
        # Создаем нового пользователя
        cur.execute("""
            INSERT INTO users (telegram_id, username, first_name, status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING id
        """, (telegram_id, username, first_name))
        conn.commit()
        
        welcome_text = f"""👋 Привет, {first_name}!

Добро пожаловать в <b>LeoMatch</b> — бот для знакомств!

Чтобы начать, заполни свою анкету:
• Возраст
• Город
• Немного о себе
• Интересы

Напиши свой возраст числом (например: 25)"""
        
        send_message(chat_id, welcome_text)
    else:
        menu_text = """🎯 <b>Главное меню</b>

Используй кнопки ниже для навигации"""
        keyboard = {
            'keyboard': [
                [{'text': '👤 Моя анкета'}, {'text': '🔍 Найти пару'}],
                [{'text': '⏸ Остановить поиск'}, {'text': '⚙️ Настройки'}]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        send_message(chat_id, menu_text, keyboard)
    
    cur.close()
    conn.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def handle_profile(chat_id: int, user_data: dict) -> dict:
    """Показать профиль пользователя"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    
    if user and user['status'] == 'active':
        profile_text = f"""👤 <b>Твоя анкета</b>

Имя: {user['first_name']}
Возраст: {user['age']} лет
Город: {user['city']}
О себе: {user['bio']}

Статус: {"✅ Верифицирован" if user['verified'] else "⏳ На модерации"}"""
        keyboard = {
            'keyboard': [
                [{'text': '🔍 Найти пару'}],
                [{'text': '🏠 Главное меню'}]
            ],
            'resize_keyboard': True
        }
        send_message(chat_id, profile_text, keyboard)
    else:
        send_message(chat_id, "Анкета не заполнена. Используй /start для регистрации.")
    
    cur.close()
    conn.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def handle_search(chat_id: int, user_data: dict) -> dict:
    """Поиск пары для пользователя"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем текущего пользователя
    cur.execute("SELECT * FROM users WHERE telegram_id = %s AND status = 'active'", (telegram_id,))
    current_user = cur.fetchone()
    
    if not current_user:
        send_message(chat_id, "Сначала заполни анкету через /start")
        cur.close()
        conn.close()
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
    
    # Ищем пользователя без активного матча
    cur.execute("""
        SELECT u.* FROM users u
        WHERE u.status = 'active' 
        AND u.verified = TRUE
        AND u.id != %s
        AND NOT EXISTS (
            SELECT 1 FROM matches m 
            WHERE (m.user1_id = %s AND m.user2_id = u.id)
            OR (m.user2_id = %s AND m.user1_id = u.id)
        )
        ORDER BY RANDOM()
        LIMIT 1
    """, (current_user['id'], current_user['id'], current_user['id']))
    
    match_user = cur.fetchone()
    
    if match_user:
        # Создаем матч
        cur.execute("""
            INSERT INTO matches (user1_id, user2_id, status)
            VALUES (%s, %s, 'active')
            RETURNING id
        """, (current_user['id'], match_user['id']))
        conn.commit()
        
        # Отправляем уведомления обоим пользователям
        match_text = f"""🎉 <b>Найдена пара!</b>

{match_user['first_name']}, {match_user['age']} лет
{match_user['city']}

{match_user['bio']}

Можешь начать общение прямо сейчас!"""
        
        keyboard = {
            'keyboard': [
                [{'text': '💬 Написать сообщение'}],
                [{'text': '⏭ Следующая анкета'}, {'text': '🏠 Главное меню'}]
            ],
            'resize_keyboard': True
        }
        send_message(chat_id, match_text, keyboard)
        send_message(match_user['telegram_id'], f"🎉 У тебя новая пара: {current_user['first_name']}!", keyboard)
    else:
        send_message(chat_id, "К сожалению, сейчас нет доступных пользователей. Попробуй позже!")
    
    cur.close()
    conn.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def handle_stop(chat_id: int, user_data: dict) -> dict:
    """Остановить активные матчи"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    
    if user:
        cur.execute("""
            UPDATE matches 
            SET status = 'closed'
            WHERE (user1_id = %s OR user2_id = %s) AND status = 'active'
        """, (user['id'], user['id']))
        conn.commit()
        keyboard = {
            'keyboard': [
                [{'text': '🔍 Найти пару'}],
                [{'text': '🏠 Главное меню'}]
            ],
            'resize_keyboard': True
        }
        send_message(chat_id, "Все активные диалоги остановлены.", keyboard)
    
    cur.close()
    conn.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def handle_message(chat_id: int, user_data: dict, text: str) -> dict:
    """Обработка обычных сообщений"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем статус пользователя
    cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    
    if not user:
        cur.close()
        conn.close()
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
    
    # Если пользователь заполняет анкету
    if user['status'] == 'pending':
        if user['age'] is None:
            # Ожидаем возраст
            try:
                age = int(text)
                if 18 <= age <= 100:
                    cur.execute("UPDATE users SET age = %s WHERE id = %s", (age, user['id']))
                    conn.commit()
                    send_message(chat_id, "✅ Отлично! Теперь напиши свой город.")
                else:
                    send_message(chat_id, "Возраст должен быть от 18 до 100 лет.")
            except ValueError:
                send_message(chat_id, "Введи возраст числом, например: 25")
        elif user['city'] is None:
            # Ожидаем город
            cur.execute("UPDATE users SET city = %s WHERE id = %s", (text, user['id']))
            conn.commit()
            send_message(chat_id, "✅ Супер! Расскажи немного о себе (интересы, хобби).")
        elif user['bio'] is None:
            # Ожидаем описание
            cur.execute("UPDATE users SET bio = %s, status = 'active' WHERE id = %s", (text, user['id']))
            conn.commit()
            success_text = "✅ Анкета заполнена! Она отправлена на модерацию.\n\nТеперь можешь искать пару!"
            keyboard = {
                'keyboard': [
                    [{'text': '🔍 Найти пару'}],
                    [{'text': '👤 Моя анкета'}, {'text': '🏠 Главное меню'}]
                ],
                'resize_keyboard': True
            }
            send_message(chat_id, success_text, keyboard)
    else:
        # Если пользователь в активном матче, пересылаем сообщение
        cur.execute("""
            SELECT m.id, m.user1_id, m.user2_id, u1.telegram_id as tid1, u2.telegram_id as tid2
            FROM matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            WHERE (m.user1_id = %s OR m.user2_id = %s) AND m.status = 'active'
            LIMIT 1
        """, (user['id'], user['id']))
        
        match = cur.fetchone()
        
        if match:
            # Сохраняем сообщение в БД
            cur.execute("""
                INSERT INTO messages (match_id, sender_id, message_text)
                VALUES (%s, %s, %s)
            """, (match['id'], user['id'], text))
            conn.commit()
            
            # Определяем получателя
            recipient_tid = match['tid2'] if match['user1_id'] == user['id'] else match['tid1']
            
            # Отправляем сообщение собеседнику
            send_message(recipient_tid, f"💬 <b>Сообщение:</b>\n\n{text}")
        else:
            keyboard = {
                'keyboard': [
                    [{'text': '🔍 Найти пару'}],
                    [{'text': '🏠 Главное меню'}]
                ],
                'resize_keyboard': True
            }
            send_message(chat_id, "У тебя нет активных диалогов. Найди пару, чтобы начать общение!", keyboard)
    
    cur.close()
    conn.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def handle_settings(chat_id: int, user_data: dict) -> dict:
    """Настройки пользователя"""
    settings_text = """⚙️ <b>Настройки</b>

Здесь ты сможешь:
• Изменить фильтры поиска
• Обновить анкету
• Настроить уведомления"""
    keyboard = {
        'keyboard': [
            [{'text': '✏️ Изменить анкету'}],
            [{'text': '🏠 Главное меню'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, settings_text, keyboard)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }


def handle_callback(callback_query: dict) -> dict:
    """Обработка нажатий на inline-кнопки"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }