import pytest

from app.exceptions import UnsupportedDocument
from app.services.resume import extract_resume, normalize_text


def test_extract_txt_and_normalize() -> None:
    assert extract_resume("cv.txt", "Опыт  работы\n\n\nPython".encode(), 1000, 100) == "Опыт работы\n\nPython"


def test_reject_extension_and_empty() -> None:
    with pytest.raises(UnsupportedDocument): extract_resume("cv.exe", b"x", 1000, 100)
    with pytest.raises(UnsupportedDocument): extract_resume("cv.txt", b"", 1000, 100)


def test_text_limit() -> None:
    assert normalize_text("abcdef", 3) == "abc"

