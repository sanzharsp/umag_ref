import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError


def validate_phone_number(phone_number: str) -> bool:
    try:
        number = phonenumbers.parse(phone_number, None)  # Используйте 'KZ' для номеров Казахстана
        return phonenumbers.is_valid_number(number)
    except NumberParseException:
        return False


def validate_email_simple(email: str) -> bool:
    try:
        # Попытка валидации электронной почты
        validate_email(email)
        return True
    except EmailNotValidError:
        # В случае ошибки валидации
        return False

