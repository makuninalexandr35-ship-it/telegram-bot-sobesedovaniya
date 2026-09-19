import importlib
import os
import unittest
from unittest.mock import patch

import bot


class BotTests(unittest.TestCase):
    def test_start_command_is_recognized(self) -> None:
        self.assertTrue(bot.is_start_command("/start"))
        self.assertTrue(bot.is_start_command("/start@InterviewBot argument"))
        self.assertFalse(bot.is_start_command("start"))

    def test_start_sends_message_to_source_chat(self) -> None:
        update = {"message": {"text": "/start", "chat": {"id": 42}}}
        with patch("bot.telegram_request") as request:
            bot.handle_update("test-token", update)
        request.assert_called_once_with(
            "test-token", "sendMessage", chat_id=42, text=bot.START_MESSAGE
        )

    def test_missing_token_is_reported(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            reloaded_bot = importlib.reload(bot)
            with self.assertRaisesRegex(RuntimeError, "TELEGRAM_BOT_TOKEN"):
                reloaded_bot.require_token()


if __name__ == "__main__":
    unittest.main()
