import importlib
import json
import os
import unittest
from unittest.mock import patch

import bot


class RequestRecorder:
    def __init__(self) -> None:
        self.calls = []

    def __call__(self, token, method, **parameters):
        self.calls.append((token, method, parameters))

    @property
    def messages(self):
        return [call[2] for call in self.calls if call[1] == "sendMessage"]


def text_update(chat_id, text):
    return {"message": {"chat": {"id": chat_id}, "text": text}}


def callback_update(chat_id, data, callback_id="callback-1"):
    return {
        "callback_query": {
            "id": callback_id,
            "data": data,
            "message": {"chat": {"id": chat_id}},
        }
    }


class BotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = RequestRecorder()
        self.bot = bot.InterviewBot("test-token", self.request)

    def test_start_shows_all_professions(self) -> None:
        self.bot.handle_update(text_update(42, "/start"))
        message = self.request.messages[-1]
        self.assertEqual(message["text"], bot.START_MESSAGE)
        keyboard = json.loads(message["reply_markup"])["inline_keyboard"]
        self.assertEqual([row[0]["text"] for row in keyboard], list(bot.QUESTIONS))
        self.assertEqual(self.bot.states[42].stage, "profession")

    def test_start_command_is_recognized(self) -> None:
        self.assertTrue(bot.is_start_command("/start"))
        self.assertTrue(bot.is_start_command("/start@InterviewBot argument"))
        self.assertFalse(bot.is_start_command("start"))

    def test_complete_interview_asks_one_question_and_returns_summary(self) -> None:
        self.bot.handle_update(text_update(42, "/start"))
        self.bot.handle_update(callback_update(42, "profession:5"))
        self.assertEqual(self.bot.states[42].profession, "Python-разработчик")
        self.assertIn("Выберите уровень", self.request.messages[-1]["text"])

        self.bot.handle_update(callback_update(42, "level:1", "callback-2"))
        self.assertEqual(self.bot.states[42].level, "Junior")
        self.assertIn("Вопрос 1 из 10", self.request.messages[-1]["text"])

        for number in range(1, 11):
            before = len(self.request.messages)
            self.bot.handle_update(text_update(42, f"Подробный ответ {number}"))
            self.assertEqual(len(self.request.messages), before + 1)

        result = self.request.messages[-1]["text"]
        self.assertIn("Отвечено вопросов: 10 из 10", result)
        self.assertIn("1. Чем изменяемые типы", result)
        self.assertIn("Ответ: Подробный ответ 10", result)
        self.assertIn("Собеседование завершено", result)
        self.assertNotIn(42, self.bot.states)

    def test_users_have_independent_state(self) -> None:
        self.bot.handle_update(text_update(1, "/start"))
        self.bot.handle_update(text_update(2, "/start"))
        self.bot.handle_update(callback_update(1, "profession:0"))
        self.assertEqual(self.bot.states[1].stage, "level")
        self.assertEqual(self.bot.states[2].stage, "profession")

    def test_text_before_selection_explains_required_action(self) -> None:
        self.bot.handle_update(text_update(42, "/start"))
        self.bot.handle_update(text_update(42, "Хочу пройти интервью"))
        self.assertIn("выберите профессию", self.request.messages[-1]["text"].lower())

    def test_cancel_and_restart_reset_progress(self) -> None:
        self.bot.handle_update(text_update(42, "/start"))
        self.bot.handle_update(callback_update(42, "profession:0"))
        self.bot.handle_update(text_update(42, "/restart"))
        self.assertEqual(self.bot.states[42], bot.InterviewState())
        self.bot.handle_update(text_update(42, "/cancel"))
        self.assertNotIn(42, self.bot.states)
        self.assertIn("прекращено", self.request.messages[-1]["text"])

    def test_stale_callback_is_handled_and_acknowledged(self) -> None:
        self.bot.handle_update(callback_update(42, "profession:0"))
        self.assertEqual(self.request.calls[0][1], "answerCallbackQuery")
        self.assertIn("неактуальна", self.request.messages[-1]["text"])

    def test_all_professions_have_ten_questions(self) -> None:
        self.assertEqual(len(bot.QUESTIONS), 6)
        for questions in bot.QUESTIONS.values():
            self.assertGreaterEqual(len(questions), 10)

    def test_missing_token_is_reported(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            reloaded_bot = importlib.reload(bot)
            with self.assertRaisesRegex(RuntimeError, "TELEGRAM_BOT_TOKEN"):
                reloaded_bot.require_token()


if __name__ == "__main__":
    unittest.main()
