"""Telegram bot for conducting practice interviews using only the stdlib."""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
START_MESSAGE = (
    "Добро пожаловать!\n"
    "Я проведу с вами тренировочное собеседование.\n\n"
    "Выберите профессию:"
)
LEVEL_MESSAGE = "Выберите уровень:"
INTRO_MESSAGE = (
    "Отлично. Начинаем собеседование.\n"
    "Я задам вам 10 вопросов по одному.\n"
    "После каждого ответа переходите к следующему вопросу."
)

QUESTIONS: dict[str, tuple[str, ...]] = {
    "Менеджер по продажам": (
        "Расскажите, как вы выявляете потребности клиента.",
        "Как вы готовитесь к первому звонку потенциальному клиенту?",
        "Как вы отвечаете на возражение «слишком дорого»?",
        "Приведите пример успешной сложной сделки.",
        "Как вы ведёте воронку продаж и расставляете приоритеты?",
        "Какие показатели эффективности продаж вы отслеживаете?",
        "Что вы делаете после отказа клиента?",
        "Как вы выстраиваете долгосрочные отношения с клиентом?",
        "Как вы выполняете план в период низкого спроса?",
        "Какую роль CRM играет в вашей ежедневной работе?",
    ),
    "SMM-специалист": (
        "Как вы разрабатываете SMM-стратегию для нового бренда?",
        "Как определить целевую аудиторию в социальных сетях?",
        "Какие метрики показывают эффективность SMM?",
        "Как вы составляете контент-план?",
        "Расскажите о кампании, результат которой вас особенно радует.",
        "Как вы реагируете на негативные комментарии?",
        "Как выбираете подходящие площадки для бренда?",
        "Как тестируете гипотезы и форматы контента?",
        "Что вы делаете при резком падении охватов?",
        "Как вы оцениваете работу с блогерами?",
    ),
    "Маркетолог": (
        "Как вы проводите исследование рынка перед запуском продукта?",
        "Как формулируете ценностное предложение?",
        "Какие метрики маркетинговой воронки вы считаете ключевыми?",
        "Как распределяете бюджет между каналами продвижения?",
        "Опишите удачный маркетинговый эксперимент из вашей практики.",
        "Как вы рассчитываете ROMI?",
        "Как сегментируете целевую аудиторию?",
        "Что предпримете, если кампания не достигает целей?",
        "Как вы взаимодействуете с отделом продаж?",
        "Как анализ конкурентов влияет на вашу стратегию?",
    ),
    "Менеджер маркетплейсов": (
        "Как вы выбираете маркетплейс для размещения товара?",
        "Как оформляете карточку товара для роста конверсии?",
        "Какие показатели кабинета продавца отслеживаете ежедневно?",
        "Как планируете поставки и предотвращаете дефицит?",
        "Как работаете с отзывами и рейтингом товара?",
        "Какими способами продвигаете товары внутри маркетплейса?",
        "Как рассчитываете юнит-экономику товара?",
        "Что предпримете при падении позиции товара в выдаче?",
        "Как анализируете ассортимент конкурентов?",
        "Как подготовитесь к сезонному росту продаж?",
    ),
    "Веб-дизайнер": (
        "Как вы начинаете работу над новым веб-проектом?",
        "Как исследуете пользователей перед созданием интерфейса?",
        "Объясните разницу между UX и UI на примере.",
        "Как выстраиваете визуальную иерархию страницы?",
        "Как проектируете адаптивный интерфейс?",
        "Как проверяете доступность дизайна?",
        "Расскажите, как вы принимаете и применяете обратную связь.",
        "Как передаёте макеты разработчикам?",
        "Как оцениваете успешность готового дизайна?",
        "Расскажите о самом сложном решении в вашем портфолио.",
    ),
    "Python-разработчик": (
        "Чем изменяемые типы данных отличаются от неизменяемых в Python?",
        "Как работают декораторы и где вы их применяли?",
        "Чем генератор отличается от обычной функции?",
        "Как вы обрабатываете исключения в приложении?",
        "Что такое контекстный менеджер?",
        "Как GIL влияет на многопоточность в CPython?",
        "Как вы тестируете Python-код?",
        "Как организуете зависимости и виртуальное окружение проекта?",
        "Как диагностируете медленно работающий участок программы?",
        "Опишите архитектуру одного из ваших Python-проектов.",
    ),
}
LEVELS = ("Стажёр", "Junior", "Middle", "Senior")


@dataclass
class InterviewState:
    """Progress of one chat's interview."""

    stage: str = "profession"
    profession: str | None = None
    level: str | None = None
    question_index: int = 0
    answers: list[str] = field(default_factory=list)


def inline_keyboard(items: list[tuple[str, str]], columns: int = 1) -> str:
    """Serialize an inline keyboard for Telegram's HTTP API."""
    rows = []
    for index in range(0, len(items), columns):
        rows.append(
            [{"text": label, "callback_data": data} for label, data in items[index:index + columns]]
        )
    return json.dumps({"inline_keyboard": rows}, ensure_ascii=False)


PROFESSION_KEYBOARD = inline_keyboard(
    [(name, f"profession:{index}") for index, name in enumerate(QUESTIONS)]
)
LEVEL_KEYBOARD = inline_keyboard(
    [(level, f"level:{index}") for index, level in enumerate(LEVELS)], columns=2
)


def require_token() -> str:
    """Return the bot token or stop with an actionable, secret-safe error."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", TOKEN or "")
    if not token or not token.strip():
        raise RuntimeError(
            "Переменная окружения TELEGRAM_BOT_TOKEN не задана. "
            "Создайте .env из .env.example и экспортируйте её перед запуском."
        )
    return token.strip()


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


def command_name(text: object) -> str | None:
    """Return a normalized Telegram command, including group-chat forms."""
    if not isinstance(text, str) or not text.strip().startswith("/"):
        return None
    command = text.strip().split(maxsplit=1)[0].lower().split("@", 1)[0]
    return command if command in {"/start", "/restart", "/cancel"} else None


def is_start_command(text: object) -> bool:
    """Recognize /start and the group-chat form /start@botname."""
    return command_name(text) == "/start"


class InterviewBot:
    """State machine and Telegram update adapter for concurrent chats."""

    def __init__(self, token: str, request: Callable[..., Any] = telegram_request):
        self.token = token
        self.request = request
        self.states: dict[int, InterviewState] = {}

    def send(self, chat_id: int, text: str, reply_markup: str | None = None) -> None:
        parameters: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup:
            parameters["reply_markup"] = reply_markup
        self.request(self.token, "sendMessage", **parameters)

    def start(self, chat_id: int) -> None:
        self.states[chat_id] = InterviewState()
        self.send(chat_id, START_MESSAGE, PROFESSION_KEYBOARD)

    def cancel(self, chat_id: int) -> None:
        if chat_id in self.states:
            del self.states[chat_id]
            self.send(chat_id, "Собеседование прекращено. Чтобы начать заново, отправьте /start.")
        else:
            self.send(chat_id, "Сейчас нет активного собеседования. Отправьте /start, чтобы начать.")

    def handle_text(self, chat_id: int, text: str) -> None:
        command = command_name(text)
        if command in {"/start", "/restart"}:
            self.start(chat_id)
            return
        if command == "/cancel":
            self.cancel(chat_id)
            return

        state = self.states.get(chat_id)
        if state is None:
            self.send(chat_id, "Сначала отправьте /start, чтобы начать собеседование.")
        elif state.stage == "profession":
            self.send(chat_id, "Сначала выберите профессию с помощью кнопки ниже.", PROFESSION_KEYBOARD)
        elif state.stage == "level":
            self.send(chat_id, "Сначала выберите уровень с помощью кнопки ниже.", LEVEL_KEYBOARD)
        elif state.stage == "interview":
            answer = text.strip()
            if not answer:
                self.send(chat_id, "Ответ не должен быть пустым. Пожалуйста, ответьте на вопрос.")
                return
            state.answers.append(answer)
            state.question_index += 1
            if state.question_index == 10:
                self.finish(chat_id, state)
            else:
                self.ask_question(chat_id, state)

    def handle_callback(self, callback: dict[str, Any]) -> None:
        callback_id = callback.get("id")
        if callback_id is not None:
            self.request(self.token, "answerCallbackQuery", callback_query_id=callback_id)
        message = callback.get("message")
        chat = message.get("chat") if isinstance(message, dict) else None
        if not isinstance(chat, dict) or not isinstance(chat.get("id"), int):
            return
        chat_id = chat["id"]
        state = self.states.get(chat_id)
        data = callback.get("data")
        if state is None:
            self.send(chat_id, "Эта кнопка уже неактуальна. Отправьте /start.")
            return

        if state.stage == "profession" and isinstance(data, str) and data.startswith("profession:"):
            try:
                profession_index = int(data.split(":", 1)[1])
                if profession_index < 0:
                    raise IndexError
                state.profession = tuple(QUESTIONS)[profession_index]
            except (ValueError, IndexError):
                self.send(chat_id, "Не удалось выбрать профессию. Используйте предложенные кнопки.")
                return
            state.stage = "level"
            self.send(chat_id, f"Профессия: {state.profession}\n\n{LEVEL_MESSAGE}", LEVEL_KEYBOARD)
            return

        if state.stage == "level" and isinstance(data, str) and data.startswith("level:"):
            try:
                level_index = int(data.split(":", 1)[1])
                if level_index < 0:
                    raise IndexError
                state.level = LEVELS[level_index]
            except (ValueError, IndexError):
                self.send(chat_id, "Не удалось выбрать уровень. Используйте предложенные кнопки.")
                return
            state.stage = "interview"
            self.send(chat_id, INTRO_MESSAGE)
            self.ask_question(chat_id, state)
            return

        prompt = "Сначала выберите профессию." if state.stage == "profession" else "Выполните текущий шаг собеседования."
        self.send(chat_id, f"Эта кнопка сейчас недоступна. {prompt}")

    def ask_question(self, chat_id: int, state: InterviewState) -> None:
        question = QUESTIONS[state.profession or ""][state.question_index]
        self.send(chat_id, f"Вопрос {state.question_index + 1} из 10:\n{question}")

    def finish(self, chat_id: int, state: InterviewState) -> None:
        questions = QUESTIONS[state.profession or ""]
        lines = [
            "Результаты тренировочного собеседования",
            f"Профессия: {state.profession}",
            f"Уровень: {state.level}",
            f"Отвечено вопросов: {len(state.answers)} из 10",
            "",
            "Вопросы и краткое резюме ответов:",
        ]
        for index, (question, answer) in enumerate(zip(questions, state.answers), 1):
            summary = " ".join(answer.split())
            if len(summary) > 180:
                summary = summary[:177].rstrip() + "..."
            lines.extend((f"{index}. {question}", f"Ответ: {summary}"))
        lines.extend(("", "Собеседование завершено. Спасибо за ваши ответы!", "Для нового интервью отправьте /restart."))
        del self.states[chat_id]
        self.send(chat_id, "\n".join(lines))

    def handle_update(self, update: dict[str, Any]) -> None:
        callback = update.get("callback_query")
        if isinstance(callback, dict):
            self.handle_callback(callback)
            return
        message = update.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("text"), str):
            return
        chat = message.get("chat")
        if isinstance(chat, dict) and isinstance(chat.get("id"), int):
            self.handle_text(chat["id"], message["text"])


_bots: dict[str, InterviewBot] = {}


def handle_update(token: str, update: dict[str, Any]) -> None:
    """Compatibility entry point that preserves state between updates."""
    bot = _bots.setdefault(token, InterviewBot(token))
    bot.handle_update(update)


def run(token: str) -> None:
    """Poll Telegram continuously and dispatch incoming updates."""
    offset = 0
    bot = InterviewBot(token)
    print("Telegram-бот запущен. Для остановки нажмите Ctrl+C.")
    while True:
        try:
            updates = telegram_request(
                token,
                "getUpdates",
                offset=offset,
                timeout=30,
                allowed_updates='["message", "callback_query"]',
            )
            for update in updates or []:
                offset = max(offset, int(update["update_id"]) + 1)
                bot.handle_update(update)
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
