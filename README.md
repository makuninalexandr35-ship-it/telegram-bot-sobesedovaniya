# Telegram-бот для собеседований

Минимальный Telegram-бот на Python, который отвечает на команду `/start`. Он
работает на стандартной библиотеке Python и не требует сторонних пакетов.

## Безопасная настройка токена

1. Создайте бота через официального [@BotFather](https://t.me/BotFather) и
   получите токен.
2. Скопируйте шаблон локальной конфигурации:

   ```bash
   cp .env.example .env
   ```

3. Впишите токен **только** в локальный файл `.env` после знака `=`. Файл
   `.env` исключён из Git. Никогда не добавляйте токен в исходный код, README,
   команды Git, логи или сообщения об ошибках.

Если токен был опубликован, немедленно отзовите его через BotFather, выпустите
новый и замените значение в окружении.

## Локальный запуск

Требуется Python 3.9 или новее. Загрузите переменные из `.env` в текущий shell
и запустите бота:

```bash
set -a
. ./.env
set +a
python3 bot.py
```

После сообщения об успешном запуске откройте чат с ботом и отправьте `/start`.
Если `TELEGRAM_BOT_TOKEN` отсутствует или пуст, программа завершится с понятной
ошибкой конфигурации. Остановить процесс можно сочетанием `Ctrl+C`.

## Запуск на сервере с systemd

1. Клонируйте репозиторий, например в `/opt/interview-bot`, и создайте отдельный
   системный аккаунт `interview-bot`.
2. Создайте файл `/etc/interview-bot.env` (он находится вне репозитория):

   ```text
   TELEGRAM_BOT_TOKEN=вставьте_токен_только_на_сервере
   ```

3. Ограничьте доступ: `sudo chmod 600 /etc/interview-bot.env`.
4. Создайте `/etc/systemd/system/interview-bot.service`:

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

5. Активируйте сервис:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now interview-bot
   sudo systemctl status interview-bot
   ```

Для production-сервера храните секрет в менеджере секретов платформы или в
закрытом `EnvironmentFile`, а не в репозитории.

## Проверки

```bash
python3 -m unittest discover -v
python3 -m compileall -q bot.py tests
```

Перед отправкой изменений убедитесь, что `.env` игнорируется:

```bash
git check-ignore .env
git status --short
```
