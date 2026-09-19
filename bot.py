"""Minimal Telegram bot implemented with Python's standard library."""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
START_MESSAGE = (
    "Привет! Я бот для подготовки к собеседованию. "
    "Отправьте мне сообщение, чтобы начать."
)


def require_token() -> str:
    """Return the bot token or stop with an actionable, secret-safe error."""
    if not TOKEN or not TOKEN.strip():
        raise RuntimeError(
            "Переменная окружения TELEGRAM_BOT_TOKEN не задана. "
            "Создайте .env из .env.example и экспортируйте её перед запуском."
        )
    return TOKEN.strip()


def telegram_request(token: str, method: str, **parameters: Any) -> Any:
    """Call a Telegram Bot API method without logging the token."""
    data = urllib.parse.urlencode(parameters).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}", data=data
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        payload = json.load(response)

    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API отклонил запрос {method}")
    return payload.get("result")


def is_start_command(text: object) -> bool:
    """Recognize /start and the group-chat form /start@botname."""
    if not isinstance(text, str):
        return False
    command = text.strip().split(maxsplit=1)[0].lower()
    return command == "/start" or command.startswith("/start@")


def handle_update(token: str, update: dict[str, Any]) -> None:
    """Handle supported commands from one Telegram update."""
    message = update.get("message")
    if not isinstance(message, dict) or not is_start_command(message.get("text")):
        return

    chat = message.get("chat")
    if isinstance(chat, dict) and chat.get("id") is not None:
        telegram_request(token, "sendMessage", chat_id=chat["id"], text=START_MESSAGE)


def run(token: str) -> None:
    """Poll Telegram continuously and dispatch incoming updates."""
    offset = 0
    print("Telegram-бот запущен. Для остановки нажмите Ctrl+C.")
    while True:
        try:
            updates = telegram_request(
                token, "getUpdates", offset=offset, timeout=30, allowed_updates='["message"]'
            )
            for update in updates or []:
                offset = max(offset, int(update["update_id"]) + 1)
                handle_update(token, update)
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, KeyError) as error:
            print(f"Ошибка связи с Telegram: {error}. Повтор через 5 секунд.", file=sys.stderr)
            time.sleep(5)


def main() -> int:
    try:
        token = require_token()
    except RuntimeError as error:
        print(f"Ошибка конфигурации: {error}", file=sys.stderr)
        return 1

    try:
        run(token)
    except KeyboardInterrupt:
        print("\nБот остановлен.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
