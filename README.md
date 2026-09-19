# Telegram-бот для тренировочных собеседований

Бот проводит последовательное интервью из 10 вопросов для одной из шести
профессий. Пользователь выбирает профессию и уровень через inline-кнопки, затем
отвечает на вопросы по одному. В конце бот показывает вопросы, краткое резюме
каждого ответа и число полученных ответов. Состояние хранится отдельно для
каждого `chat_id`, поэтому несколько пользователей могут проходить интервью
одновременно.

Проект использует только стандартную библиотеку Python и Telegram Bot API через
long polling. Сторонние зависимости и `requirements.txt` не нужны.

## Команды

- `/start` — начать интервью;
- `/restart` — сбросить текущий прогресс и начать заново;
- `/cancel` — прекратить текущее интервью.

Состояние хранится в памяти процесса: после перезапуска программы незавершённые
интервью будут сброшены.

## Безопасная настройка токена

1. Создайте бота через официального [@BotFather](https://t.me/BotFather) и
   получите токен.
2. Скопируйте шаблон локальной конфигурации:

   ```bash
   cp .env.example .env
   ```

3. Впишите токен **только** в локальный файл `.env` после знака `=`. Файл
   `.env` исключён из Git. Никогда не добавляйте токен в код, README, команды
   Git, логи или сообщения об ошибках.

Если токен был опубликован, немедленно отзовите его через BotFather и выпустите
новый.

## Локальный запуск

Требуется Python 3.10 или новее. Загрузите переменную окружения из `.env` и
запустите основной файл:

```bash
set -a
. ./.env
set +a
python bot.py
```

При отсутствии или пустом значении `TELEGRAM_BOT_TOKEN` программа завершится с
понятной ошибкой, не раскрывающей секрет. Для остановки нажмите `Ctrl+C`.

## Запуск на сервере с systemd

Создайте защищённый файл `/etc/interview-bot.env` вне репозитория:

```text
TELEGRAM_BOT_TOKEN=вставьте_токен_только_на_сервере
```

Ограничьте доступ командой `sudo chmod 600 /etc/interview-bot.env`, а затем
создайте `/etc/systemd/system/interview-bot.service`:

```ini
[Unit]
Description=Telegram interview bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=interview-bot
WorkingDirectory=/opt/interview-bot
EnvironmentFile=/etc/interview-bot.env
ExecStart=/usr/bin/python3 /opt/interview-bot/bot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now interview-bot
sudo systemctl status interview-bot
```

## Проверки

```bash
python -m unittest discover -v
python -m compileall -q bot.py tests
```

Чтобы убедиться, что локальный секрет не попадёт в коммит:

```bash
git check-ignore .env
git status --short
```
