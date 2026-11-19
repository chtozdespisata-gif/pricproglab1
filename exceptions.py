class PlatformError(Exception):
    """Базовая ошибка платформы."""


class NotFoundError(PlatformError):
    """Объект не найден по ID."""


class InputDataError(PlatformError):
    """Ошибка в переданных данных."""
