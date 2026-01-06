# Инструкция по загрузке проекта на GitHub

## Шаг 1: Инициализация Git репозитория

```bash
cd /Users/rudique/Code/audio_bot

# Инициализируем git (если еще не сделано)
git init

# Проверяем какие файлы будут добавлены
git status
```

## Шаг 2: Первый коммит

```bash
# Добавляем все файлы
git add .

# Создаем первый коммит
git commit -m "Initial commit: Telegram audio bot with Faster-Whisper

Features:
- Voice message recognition using Faster-Whisper
- Audio file recognition support
- Docker deployment support
- Russian language support
- Async processing with ThreadPoolExecutor"

# Проверяем что коммит создан
git log --oneline
```

## Шаг 3: Создание репозитория на GitHub

1. Откройте [github.com](https://github.com) и войдите в аккаунт
2. Нажмите на кнопку "+" в правом верхнем углу → "New repository"
3. Заполните форму:
   - **Repository name**: `audio_bot` (или другое название)
   - **Description**: "Telegram bot for audio/voice message recognition using Faster-Whisper"
   - **Public** или **Private** (на ваш выбор)
   - ⚠️ **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license"
4. Нажмите "Create repository"

## Шаг 4: Подключение к GitHub

GitHub покажет команды для подключения. Выполните их:

```bash
# Добавляем remote репозиторий (замените YOUR_USERNAME на ваш username)
git remote add origin git@github.com:YOUR_USERNAME/audio_bot.git

# ИЛИ если используете HTTPS:
git remote add origin https://github.com/YOUR_USERNAME/audio_bot.git

# Проверяем что remote добавлен
git remote -v
```

## Шаг 5: Загрузка кода на GitHub

```bash
# Переименовываем ветку в main (если нужно)
git branch -M main

# Загружаем код на GitHub
git push -u origin main
```

### Если возникла ошибка с SSH ключом:

```bash
# Проверьте есть ли у вас SSH ключ
ls -la ~/.ssh

# Если нет id_rsa.pub или id_ed25519.pub, создайте новый ключ:
ssh-keygen -t ed25519 -C "your_email@example.com"

# Скопируйте публичный ключ
cat ~/.ssh/id_ed25519.pub

# Добавьте этот ключ на GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key
```

### Альтернативно используйте HTTPS:

```bash
# Если SSH не работает, используйте HTTPS
git remote set-url origin https://github.com/YOUR_USERNAME/audio_bot.git
git push -u origin main

# Введите username и personal access token (не пароль!)
```

## Шаг 6: Проверка

1. Обновите страницу репозитория на GitHub
2. Вы должны увидеть все ваши файлы
3. Убедитесь что файл `.env` **НЕ** загружен (он в .gitignore)

## Дальнейшая работа с Git

### Добавление изменений:

```bash
# Проверяем изменения
git status

# Добавляем все изменения
git add .

# Или добавляем конкретные файлы
git add bot.py speech_recognition.py

# Создаем коммит
git commit -m "Описание изменений"

# Загружаем на GitHub
git push
```

### Получение изменений с GitHub:

```bash
# Загружаем последние изменения
git pull origin main
```

### Полезные команды:

```bash
# История коммитов
git log --oneline --graph

# Посмотреть изменения в файле
git diff bot.py

# Отменить изменения в файле (до git add)
git checkout -- bot.py

# Посмотреть remote репозиторий
git remote -v

# Посмотреть текущую ветку
git branch
```

## Настройка Personal Access Token для HTTPS

Если используете HTTPS, вам нужен Personal Access Token:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Generate new token (classic)
3. Заполните:
   - **Note**: "Audio Bot Development"
   - **Expiration**: 90 days (или больше)
   - **Scopes**: выберите `repo` (это даст полный доступ к приватным репозиториям)
4. Нажмите "Generate token"
5. **ВАЖНО**: Скопируйте токен сразу! Вы не сможете увидеть его снова
6. Используйте этот токен вместо пароля при `git push`

## Клонирование репозитория на сервер

После загрузки на GitHub, вы можете клонировать репозиторий на сервер:

```bash
# На сервере:
git clone https://github.com/YOUR_USERNAME/audio_bot.git
cd audio_bot
```

Или используйте автоматический скрипт деплоя:

```bash
# На локальной машине:
./deploy.sh user@server-ip
```

## Troubleshooting

### "Permission denied (publickey)"
- Проблема с SSH ключом
- Решение: используйте HTTPS или настройте SSH ключ

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin git@github.com:YOUR_USERNAME/audio_bot.git
```

### "refusing to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
```

### Случайно закоммитили .env файл
```bash
# Удалите файл из git (но оставьте локально)
git rm --cached .env
git commit -m "Remove .env from repository"
git push

# Если .env уже в истории, лучше создать новый BOT_TOKEN
# т.к. старый теперь публичный
```
