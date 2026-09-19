from app.services.interview import normalize_question


def test_normalization_detects_simple_repeat() -> None:
    assert normalize_question("Расскажите о себе?") == normalize_question("РАССКАЖИТЕ, о себе!")
