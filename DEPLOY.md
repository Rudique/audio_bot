# Инструкция по развертыванию бота на сервере

## Шаг 1: Подготовка на локальной машине

### 1.1. Инициализация Git репозитория

```bash
# Инициализируем git (если еще не сделано)
cd /Users/rudique/Code/audio_bot
git init

# Добавляем все файлы
git add .

# Создаем первый коммит
git commit -m "Initial commit: Telegram audio bot with Faster-Whisper"
```

### 1.2. Создание репозитория на GitHub

1. Зайдите на [github.com](https://github.com) и создайте новый репозиторий
2. **НЕ** добавляйте README, .gitignore или LICENSE (они уже есть в проекте)
3. Скопируйте URL репозитория (например: `git@github.com:username/audio_bot.git`)

### 1.3. Загрузка кода на GitHub

```bash
# Добавляем remote репозиторий
git remote add origin git@github.com:ваш-username/audio_bot.git

# Отправляем код на GitHub
git branch -M main
git push -u origin main
```

## Шаг 2: Подготовка сервера

### 2.1. Подключение к серверу

```bash
ssh user@your-server-ip
```

### 2.2. Установка Docker и Docker Compose

**Ubuntu/Debian:**

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo apt install docker-compose-plugin -y

# Перелогиниваемся для применения изменений
exit
ssh user@your-server-ip

# Проверяем установку
docker --version
docker compose version
```

**CentOS/RHEL:**

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

## Шаг 3: Развертывание бота на сервере

### 3.1. Клонирование репозитория

```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем репозиторий
git clone git@github.com:ваш-username/audio_bot.git

# Или через HTTPS если нет SSH ключа:
# git clone https://github.com/ваш-username/audio_bot.git

# Переходим в директорию проекта
cd audio_bot
```

### 3.2. Настройка переменных окружения

```bash
# Создаем файл .env
nano .env

# Или используйте vim:
# vim .env
```

Добавьте в файл:
```
BOT_TOKEN=your_actual_bot_token_here
```

Сохраните файл (Ctrl+X, затем Y, затем Enter в nano)

### 3.3. Запуск бота

```bash
# Собираем и запускаем контейнер
docker compose up -d

# Проверяем статус
docker compose ps

# Смотрим логи
docker compose logs -f
```

Бот запущен! При первом запуске скачается модель Whisper (~150 MB).

## Шаг 4: Управлениеботом

### Просмотр логов

```bash
# Все логи
docker compose logs -f

# Последние 100 строк
docker compose logs --tail=100

# Логи за последний час
docker compose logs --since 1h
```

### Перезапуск бота

```bash
docker compose restart
```

### Остановка бота

```bash
docker compose stop
```

### Полная остановка и удаление контейнера

```bash
docker compose down
```

### Обновление бота

```bash
# Останавливаем контейнер
docker compose down

# Получаем последние изменения из GitHub
git pull origin main

# Пересобираем и запускаем
docker compose up -d --build

# Проверяем логи
docker compose logs -f
```

## Шаг 5: Настройка автозапуска

Docker контейнер уже настроен с `restart: unless-stopped`, поэтому он:
- Автоматически запустится при перезагрузке сервера
- Перезапустится при падении
- НЕ запустится, если вы его остановили вручную

## Шаг 6: Мониторинг

### Проверка использования ресурсов

```bash
# Статистика контейнера
docker stats telegram-audio-bot

# Использование диска
docker system df
```

### Проверка работоспособности

```bash
# Проверяем что контейнер работает
docker compose ps

# Если статус не "Up" - смотрим логи
docker compose logs --tail=50
```

## Решение проблем

### Бот не запускается

```bash
# Проверьте логи
docker compose logs

# Проверьте .env файл
cat .env

# Пересоздайте контейнер
docker compose down
docker compose up -d --build
```

### Недостаточно памяти

Отредактируйте `docker-compose.yml`, измените лимиты:

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Увеличьте если нужно
```

Затем:
```bash
docker compose down
docker compose up -d
```

### Очистка диска

```bash
# Удаление неиспользуемых образов и контейнеров
docker system prune -a

# Будьте осторожны - это удалит ВСЕ неиспользуемые данные Docker
```

## Безопасность

1. **Никогда не коммитьте .env файл в Git** (уже в .gitignore)
2. **Используйте SSH ключи** для доступа к серверу
3. **Настройте firewall** на сервере
4. **Регулярно обновляйте** систему и Docker

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker compose pull
docker compose up -d
```

## Дополнительные настройки

### Изменение модели Whisper

Отредактируйте `speech_recognition.py:19` и измените:
- `tiny` - быстрее, менее точно
- `base` - по умолчанию
- `small` - точнее, медленнее
- `medium` - очень точно, требует больше RAM

После изменения:
```bash
git add speech_recognition.py
git commit -m "Change Whisper model to small"
git push origin main

# На сервере:
git pull origin main
docker compose up -d --build
```

## Полезные команды

```bash
# Зайти внутрь контейнера
docker compose exec audio-bot bash

# Посмотреть переменные окружения
docker compose exec audio-bot env

# Скопировать файл из контейнера
docker compose cp audio-bot:/app/temp/file.ogg ./

# Посмотреть все Docker образы
docker images

# Удалить старые образы
docker image prune -a
```
