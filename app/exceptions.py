class AppError(Exception):
    """Безопасная базовая ошибка приложения."""


class InvalidAIResponse(AppError):
    pass


class AIUnavailable(AppError):
    pass


class InterviewStateError(AppError):
    pass


class UnsupportedDocument(AppError):
    pass


class AccessDenied(AppError):
    pass

