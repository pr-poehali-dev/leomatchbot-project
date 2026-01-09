-- Добавляем поддержку множественных медиафайлов для анкет

-- Таблица для хранения фото/видео пользователей
CREATE TABLE IF NOT EXISTS user_media (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    media_type VARCHAR(10) NOT NULL CHECK (media_type IN ('photo', 'video')),
    file_id VARCHAR(255) NOT NULL,
    file_url TEXT,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_media_user_id ON user_media(user_id);

-- Таблица для лайков/дизлайков
CREATE TABLE IF NOT EXISTS user_reactions (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER NOT NULL,
    to_user_id INTEGER NOT NULL,
    reaction_type VARCHAR(10) NOT NULL CHECK (reaction_type IN ('like', 'dislike')),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_user_id, to_user_id)
);

CREATE INDEX idx_user_reactions_from_user ON user_reactions(from_user_id);
CREATE INDEX idx_user_reactions_to_user ON user_reactions(to_user_id);

-- Обновляем таблицу матчей для взаимных симпатий
ALTER TABLE matches ADD COLUMN IF NOT EXISTS matched_at TIMESTAMP;

-- Таблица для состояния заполнения анкеты
CREATE TABLE IF NOT EXISTS user_registration_state (
    telegram_id BIGINT PRIMARY KEY,
    current_step VARCHAR(50) DEFAULT 'age',
    temp_data JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);