#!/bin/bash

# Скрипт для быстрого деплоя бота на сервер

set -e  # Остановка при ошибке

echo "🚀 Деплой Telegram Audio Bot"
echo "================================"

# Проверяем что передан адрес сервера
if [ -z "$1" ]; then
    echo "❌ Ошибка: не указан адрес сервера"
    echo "Использование: ./deploy.sh user@server-ip [путь-на-сервере]"
    echo "Пример: ./deploy.sh root@192.168.1.100 /opt/audio_bot"
    exit 1
fi

SERVER=$1
REMOTE_PATH=${2:-~/audio_bot}

echo "📡 Сервер: $SERVER"
echo "📁 Путь на сервере: $REMOTE_PATH"
echo ""

# Проверяем подключение к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=5 "$SERVER" "echo 'Подключение успешно'" > /dev/null 2>&1; then
    echo "❌ Не удалось подключиться к серверу $SERVER"
    exit 1
fi
echo "✅ Подключение установлено"
echo ""

# Проверяем что Docker установлен на сервере
echo "🐳 Проверка Docker на сервере..."
if ! ssh "$SERVER" "docker --version" > /dev/null 2>&1; then
    echo "⚠️  Docker не установлен на сервере"
    echo "Хотите установить Docker? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "📦 Установка Docker..."
        ssh "$SERVER" "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
        echo "✅ Docker установлен"
    else
        echo "❌ Docker необходим для работы. Установите его вручную."
        exit 1
    fi
else
    echo "✅ Docker установлен"
fi
echo ""

# Создаем директорию на сервере если её нет
echo "📁 Создание директории на сервере..."
ssh "$SERVER" "mkdir -p $REMOTE_PATH"
echo "✅ Директория создана"
echo ""

# Копируем файлы на сервер (исключая ненужные)
echo "📤 Копирование файлов на сервер..."
rsync -avz --progress \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='temp/' \
    --exclude='.git' \
    --exclude='.env' \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    ./ "$SERVER:$REMOTE_PATH/"
echo "✅ Файлы скопированы"
echo ""

# Проверяем наличие .env файла на сервере
echo "🔐 Проверка .env файла..."
if ! ssh "$SERVER" "test -f $REMOTE_PATH/.env"; then
    echo "⚠️  Файл .env не найден на сервере"
    echo "Введите BOT_TOKEN для бота:"
    read -r BOT_TOKEN
    if [ -z "$BOT_TOKEN" ]; then
        echo "❌ BOT_TOKEN не может быть пустым"
        exit 1
    fi
    ssh "$SERVER" "echo 'BOT_TOKEN=$BOT_TOKEN' > $REMOTE_PATH/.env"
    echo "✅ Файл .env создан"
else
    echo "✅ Файл .env уже существует"
fi
echo ""

# Запуск/перезапуск бота на сервере
echo "🚀 Запуск бота..."
ssh "$SERVER" "cd $REMOTE_PATH && docker compose down && docker compose up -d --build"
echo "✅ Бот запущен"
echo ""

# Показываем логи
echo "📋 Последние логи:"
ssh "$SERVER" "cd $REMOTE_PATH && docker compose logs --tail=20"
echo ""

echo "================================"
echo "✅ Деплой завершен успешно!"
echo ""
echo "Полезные команды:"
echo "  Просмотр логов:   ssh $SERVER 'cd $REMOTE_PATH && docker compose logs -f'"
echo "  Перезапуск:       ssh $SERVER 'cd $REMOTE_PATH && docker compose restart'"
echo "  Остановка:        ssh $SERVER 'cd $REMOTE_PATH && docker compose stop'"
echo "  Статус:           ssh $SERVER 'cd $REMOTE_PATH && docker compose ps'"
