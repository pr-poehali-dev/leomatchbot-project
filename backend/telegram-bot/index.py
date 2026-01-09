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
        
        # Обработка callback_query (нажатия на кнопки)
        callback_query = body.get('callback_query')
        if callback_query:
            return handle_callback(callback_query)
        
        # Обработка сообщений
        message = body.get('message', {})
        if not message:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user_data = message.get('from', {})
        photo = message.get('photo')
        video = message.get('video')
        
        if not chat_id:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
        
        # Обработка фото/видео
        if photo or video:
            return handle_media(chat_id, user_data, photo, video)
        
        # Обработка команд
        if text.startswith('/start'):
            return handle_start(chat_id, user_data)
        elif text == '👤 Моя анкета':
            return handle_profile(chat_id, user_data)
        elif text == '🔍 Найти пару':
            return handle_search(chat_id, user_data)
        elif text == '⏸ Остановить поиск':
            return handle_pause_profile(chat_id, user_data)
        elif text == '⚙️ Настройки':
            return handle_settings(chat_id, user_data)
        else:
            # Обработка текста (заполнение анкеты или сообщение)
            return handle_text(chat_id, user_data, text)
        
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
        payload['reply_markup'] = json.dumps(reply_markup)
    
    requests.post(url, json=payload)


def send_photo(chat_id: int, photo_file_id: str, caption: str = '', reply_markup=None):
    """Отправка фото через Telegram API"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    payload = {
        'chat_id': chat_id,
        'photo': photo_file_id,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    requests.post(url, json=payload)


def send_video(chat_id: int, video_file_id: str, caption: str = '', reply_markup=None):
    """Отправка видео через Telegram API"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    payload = {
        'chat_id': chat_id,
        'video': video_file_id,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    requests.post(url, json=payload)


def handle_start(chat_id: int, user_data: dict) -> dict:
    """Обработка команды /start"""
    telegram_id = user_data.get('id')
    username = user_data.get('username', '')
    first_name = user_data.get('first_name', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    # Проверяем, есть ли пользователь в БД
    cur.execute(f"SELECT * FROM {schema}.users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    
    if not user:
        # Создаем нового пользователя
        cur.execute(f"""
            INSERT INTO {schema}.users (telegram_id, username, first_name, status, verified)
            VALUES (%s, %s, %s, 'pending', TRUE)
            RETURNING id
        """, (telegram_id, username, first_name))
        conn.commit()
        
        # Сохраняем состояние регистрации
        cur.execute(f"""
            INSERT INTO {schema}.user_registration_state (telegram_id, current_step)
            VALUES (%s, 'age')
            ON CONFLICT (telegram_id) DO UPDATE SET current_step = 'age', updated_at = CURRENT_TIMESTAMP
        """, (telegram_id,))
        conn.commit()
        
        welcome_text = f"""👋 Привет, {first_name}!

Добро пожаловать в <b>LeoMatch</b> — бот для знакомств!

Давай создадим твою анкету. Начнем с простого:

📅 <b>Напиши свой возраст</b> (например: 25)"""
        
        send_message(chat_id, welcome_text)
    else:
        if user['status'] == 'paused':
            # Возобновляем анкету
            cur.execute(f"UPDATE {schema}.users SET status = 'active' WHERE telegram_id = %s", (telegram_id,))
            conn.commit()
            send_message(chat_id, "✅ Анкета активирована! Можешь начинать поиск.")
        
        show_main_menu(chat_id)
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def show_main_menu(chat_id: int):
    """Показать главное меню"""
    menu_text = """🎯 <b>Главное меню</b>

Выбери действие:"""
    keyboard = {
        'keyboard': [
            [{'text': '👤 Моя анкета'}, {'text': '🔍 Найти пару'}],
            [{'text': '⏸ Остановить поиск'}, {'text': '⚙️ Настройки'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    send_message(chat_id, menu_text, keyboard)


def handle_text(chat_id: int, user_data: dict, text: str) -> dict:
    """Обработка текстовых сообщений"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    # Проверяем состояние регистрации
    cur.execute(f"SELECT * FROM {schema}.user_registration_state WHERE telegram_id = %s", (telegram_id,))
    reg_state = cur.fetchone()
    
    if reg_state:
        # Пользователь заполняет анкету
        step = reg_state['current_step']
        temp_data = reg_state['temp_data'] or {}
        
        if step == 'age':
            # Валидация возраста
            try:
                age = int(text)
                if age < 18 or age > 100:
                    send_message(chat_id, "❌ Возраст должен быть от 18 до 100 лет. Попробуй еще раз:")
                    cur.close()
                    conn.close()
                    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
                
                temp_data['age'] = age
                cur.execute(f"""
                    UPDATE {schema}.user_registration_state 
                    SET current_step = 'gender', temp_data = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_id = %s
                """, (json.dumps(temp_data), telegram_id))
                conn.commit()
                
                keyboard = {
                    'keyboard': [[{'text': '👨 Мужской'}, {'text': '👩 Женский'}]],
                    'resize_keyboard': True,
                    'one_time_keyboard': True
                }
                send_message(chat_id, "👫 <b>Выбери свой пол:</b>", keyboard)
                
            except ValueError:
                send_message(chat_id, "❌ Введи возраст цифрами (например: 25)")
        
        elif step == 'gender':
            gender = 'male' if '👨' in text or 'муж' in text.lower() else 'female'
            temp_data['gender'] = gender
            cur.execute(f"""
                UPDATE {schema}.user_registration_state 
                SET current_step = 'city', temp_data = %s, updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = %s
            """, (json.dumps(temp_data), telegram_id))
            conn.commit()
            
            send_message(chat_id, "🏙 <b>Напиши свой город:</b>\n(например: Москва)")
        
        elif step == 'city':
            temp_data['city'] = text
            cur.execute(f"""
                UPDATE {schema}.user_registration_state 
                SET current_step = 'bio', temp_data = %s, updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = %s
            """, (json.dumps(temp_data), telegram_id))
            conn.commit()
            
            send_message(chat_id, "📝 <b>Расскажи немного о себе:</b>\n(хобби, интересы, чем занимаешься)")
        
        elif step == 'bio':
            temp_data['bio'] = text
            cur.execute(f"""
                UPDATE {schema}.user_registration_state 
                SET current_step = 'photo', temp_data = %s, updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = %s
            """, (json.dumps(temp_data), telegram_id))
            conn.commit()
            
            send_message(chat_id, "📸 <b>Загрузи свои фото</b> (до 2 штук)\n\nОтправь первое фото:")
        
        elif step == 'photo' or step == 'video':
            send_message(chat_id, "📷 Пожалуйста, отправь фото или видео (не текст)")
    
    else:
        # Возможно это сообщение в чате с матчем
        # TODO: отправка сообщения в активный чат
        send_message(chat_id, "Используй меню для навигации")
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def handle_media(chat_id: int, user_data: dict, photo, video) -> dict:
    """Обработка загруженных фото/видео"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    # Проверяем состояние регистрации
    cur.execute(f"SELECT * FROM {schema}.user_registration_state WHERE telegram_id = %s", (telegram_id,))
    reg_state = cur.fetchone()
    
    if not reg_state:
        send_message(chat_id, "Сначала начни регистрацию командой /start")
        cur.close()
        conn.close()
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
    
    step = reg_state['current_step']
    
    # Получаем user_id
    cur.execute(f"SELECT id FROM {schema}.users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
    
    user_id = user['id']
    
    # Подсчитываем загруженные медиа
    cur.execute(f"SELECT COUNT(*) as count FROM {schema}.user_media WHERE user_id = %s AND media_type = 'photo'", (user_id,))
    photo_count = cur.fetchone()['count']
    
    cur.execute(f"SELECT COUNT(*) as count FROM {schema}.user_media WHERE user_id = %s AND media_type = 'video'", (user_id,))
    video_count = cur.fetchone()['count']
    
    if photo and step == 'photo':
        if photo_count >= 2:
            keyboard = {
                'inline_keyboard': [[
                    {'text': '✅ Завершить', 'callback_data': 'finish_registration'},
                    {'text': '🎥 Добавить видео', 'callback_data': 'add_video'}
                ]]
            }
            send_message(chat_id, "У тебя уже есть 2 фото. Можешь добавить короткое видео или завершить регистрацию:", keyboard)
        else:
            # Сохраняем фото
            file_id = photo[-1]['file_id']  # Берем самое большое фото
            cur.execute(f"""
                INSERT INTO {schema}.user_media (user_id, media_type, file_id, position)
                VALUES (%s, 'photo', %s, %s)
            """, (user_id, file_id, photo_count))
            conn.commit()
            
            if photo_count == 0:
                send_message(chat_id, "✅ Отлично! Можешь отправить еще одно фото или перейти к видео.")
            else:
                keyboard = {
                    'inline_keyboard': [[
                        {'text': '✅ Завершить', 'callback_data': 'finish_registration'},
                        {'text': '🎥 Добавить видео', 'callback_data': 'add_video'}
                    ]]
                }
                send_message(chat_id, "✅ Отлично! Можешь добавить короткое видео или завершить регистрацию:", keyboard)
    
    elif video and (step == 'photo' or step == 'video'):
        if video_count >= 1:
            send_message(chat_id, "❌ Можно добавить только 1 видео")
        else:
            file_id = video['file_id']
            cur.execute(f"""
                INSERT INTO {schema}.user_media (user_id, media_type, file_id, position)
                VALUES (%s, 'video', %s, 0)
            """, (user_id, file_id))
            conn.commit()
            
            keyboard = {
                'inline_keyboard': [[
                    {'text': '✅ Завершить регистрацию', 'callback_data': 'finish_registration'}
                ]]
            }
            send_message(chat_id, "✅ Видео добавлено! Теперь завершим регистрацию:", keyboard)
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def handle_callback(callback_query: dict) -> dict:
    """Обработка нажатий на inline-кнопки"""
    data = callback_query.get('data')
    user_data = callback_query.get('from', {})
    telegram_id = user_data.get('id')
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    if data == 'finish_registration':
        # Завершаем регистрацию
        cur.execute(f"SELECT * FROM {schema}.user_registration_state WHERE telegram_id = %s", (telegram_id,))
        reg_state = cur.fetchone()
        
        if reg_state:
            temp_data = reg_state['temp_data'] or {}
            
            # Обновляем пользователя
            cur.execute(f"""
                UPDATE {schema}.users 
                SET age = %s, gender = %s, city = %s, bio = %s, status = 'active'
                WHERE telegram_id = %s
            """, (temp_data.get('age'), temp_data.get('gender'), temp_data.get('city'), temp_data.get('bio'), telegram_id))
            
            # Удаляем состояние регистрации
            cur.execute(f"DELETE FROM {schema}.user_registration_state WHERE telegram_id = %s", (telegram_id,))
            conn.commit()
            
            send_message(chat_id, "🎉 <b>Анкета создана!</b>\n\nТеперь ты можешь искать пару!")
            show_main_menu(chat_id)
    
    elif data == 'add_video':
        cur.execute(f"""
            UPDATE {schema}.user_registration_state 
            SET current_step = 'video', updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = %s
        """, (telegram_id,))
        conn.commit()
        send_message(chat_id, "🎥 Отправь короткое видео (до 1 минуты)")
    
    elif data.startswith('like_') or data.startswith('dislike_'):
        # Обработка лайка/дизлайка
        reaction_type = 'like' if data.startswith('like_') else 'dislike'
        target_user_id = int(data.split('_')[1])
        
        cur.execute(f"SELECT id FROM {schema}.users WHERE telegram_id = %s", (telegram_id,))
        from_user = cur.fetchone()
        
        if from_user:
            # Сохраняем реакцию
            cur.execute(f"""
                INSERT INTO {schema}.user_reactions (from_user_id, to_user_id, reaction_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (from_user_id, to_user_id) DO UPDATE SET reaction_type = %s
            """, (from_user['id'], target_user_id, reaction_type, reaction_type))
            conn.commit()
            
            if reaction_type == 'like':
                # Проверяем взаимную симпатию
                cur.execute(f"""
                    SELECT * FROM {schema}.user_reactions 
                    WHERE from_user_id = %s AND to_user_id = %s AND reaction_type = 'like'
                """, (target_user_id, from_user['id']))
                mutual_like = cur.fetchone()
                
                if mutual_like:
                    # Создаем матч
                    cur.execute(f"""
                        INSERT INTO {schema}.matches (user1_id, user2_id, status, matched_at)
                        VALUES (%s, %s, 'active', CURRENT_TIMESTAMP)
                    """, (from_user['id'], target_user_id))
                    conn.commit()
                    
                    # Уведомляем обоих
                    cur.execute(f"SELECT * FROM {schema}.users WHERE id = %s", (target_user_id,))
                    target_user = cur.fetchone()
                    
                    send_message(chat_id, f"💘 <b>Взаимная симпатия!</b>\n\nВы понравились друг другу! Можете начать общение.")
                    send_message(target_user['telegram_id'], f"💘 <b>Взаимная симпатия!</b>\n\nВы понравились друг другу! Можете начать общение.")
                else:
                    send_message(chat_id, "👍 Лайк отправлен! Если будет взаимность — мы сообщим.")
            else:
                send_message(chat_id, "👎 Понятно, ищем дальше...")
            
            # Показываем следующую анкету
            show_next_profile(chat_id, telegram_id)
    
    elif data.startswith('delete_profile'):
        # Удаление анкеты
        cur.execute(f"DELETE FROM {schema}.users WHERE telegram_id = %s", (telegram_id,))
        conn.commit()
        send_message(chat_id, "🗑 Анкета удалена. Используй /start для создания новой.")
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def show_next_profile(chat_id: int, telegram_id: int):
    """Показать следующую анкету для оценки"""
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    # Получаем текущего пользователя
    cur.execute(f"SELECT * FROM {schema}.users WHERE telegram_id = %s", (telegram_id,))
    current_user = cur.fetchone()
    
    if not current_user:
        cur.close()
        conn.close()
        return
    
    # Ищем анкеты, которые пользователь еще не оценил
    cur.execute(f"""
        SELECT u.* FROM {schema}.users u
        WHERE u.id != %s 
        AND u.status = 'active'
        AND NOT EXISTS (
            SELECT 1 FROM {schema}.user_reactions r 
            WHERE r.from_user_id = %s AND r.to_user_id = u.id
        )
        ORDER BY RANDOM()
        LIMIT 1
    """, (current_user['id'], current_user['id']))
    
    next_user = cur.fetchone()
    
    if not next_user:
        send_message(chat_id, "😔 Пока нет новых анкет. Попробуй позже!")
        cur.close()
        conn.close()
        return
    
    # Получаем медиа пользователя
    cur.execute(f"""
        SELECT * FROM {schema}.user_media 
        WHERE user_id = %s 
        ORDER BY media_type, position
    """, (next_user['id'],))
    media_files = cur.fetchall()
    
    # Формируем текст анкеты
    profile_text = f"""👤 <b>{next_user['first_name']}, {next_user['age']}</b>
📍 {next_user['city']}

{next_user['bio']}"""
    
    keyboard = {
        'inline_keyboard': [[
            {'text': '❌ Дизлайк', 'callback_data': f"dislike_{next_user['id']}"},
            {'text': '💚 Лайк', 'callback_data': f"like_{next_user['id']}"}
        ]]
    }
    
    # Отправляем медиа
    if media_files:
        for media in media_files:
            if media['media_type'] == 'photo':
                if media == media_files[-1]:  # Последнее фото — с текстом и кнопками
                    send_photo(chat_id, media['file_id'], profile_text, keyboard)
                else:
                    send_photo(chat_id, media['file_id'])
            elif media['media_type'] == 'video':
                send_video(chat_id, media['file_id'], profile_text, keyboard)
    else:
        send_message(chat_id, profile_text, keyboard)
    
    cur.close()
    conn.close()


def handle_search(chat_id: int, user_data: dict) -> dict:
    """Начать поиск пары"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    cur.execute(f"SELECT * FROM {schema}.users WHERE telegram_id = %s AND status = 'active'", (telegram_id,))
    user = cur.fetchone()
    
    if not user:
        send_message(chat_id, "❌ Сначала заполни анкету через /start")
        cur.close()
        conn.close()
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
    
    send_message(chat_id, "🔍 Ищем анкеты...")
    show_next_profile(chat_id, telegram_id)
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def handle_profile(chat_id: int, user_data: dict) -> dict:
    """Показать профиль пользователя"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    cur.execute(f"SELECT * FROM {schema}.users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    
    if user and user['status'] in ['active', 'paused']:
        status_text = "✅ Активна" if user['status'] == 'active' else "⏸ Приостановлена"
        
        profile_text = f"""👤 <b>Твоя анкета</b>

Имя: {user['first_name']}
Возраст: {user['age']} лет
Пол: {'👨 Мужской' if user['gender'] == 'male' else '👩 Женский'}
Город: {user['city']}
О себе: {user['bio']}

Статус: {status_text}"""
        
        keyboard = {
            'inline_keyboard': [
                [{'text': '🗑 Удалить анкету', 'callback_data': 'delete_profile'}]
            ]
        }
        send_message(chat_id, profile_text, keyboard)
    else:
        send_message(chat_id, "❌ Анкета не заполнена. Используй /start")
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def handle_pause_profile(chat_id: int, user_data: dict) -> dict:
    """Приостановить показ анкеты"""
    telegram_id = user_data.get('id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    schema = os.environ.get('MAIN_DB_SCHEMA', 'public')
    
    cur.execute(f"UPDATE {schema}.users SET status = 'paused' WHERE telegram_id = %s", (telegram_id,))
    conn.commit()
    
    send_message(chat_id, "⏸ Поиск остановлен. Твоя анкета скрыта.\n\nИспользуй /start чтобы возобновить.")
    
    cur.close()
    conn.close()
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}


def handle_settings(chat_id: int, user_data: dict) -> dict:
    """Настройки профиля"""
    keyboard = {
        'inline_keyboard': [
            [{'text': '🗑 Удалить анкету навсегда', 'callback_data': 'delete_profile'}]
        ]
    }
    send_message(chat_id, "⚙️ <b>Настройки</b>\n\nВыбери действие:", keyboard)
    
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
