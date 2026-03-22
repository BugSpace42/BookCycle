"""
Модуль utils.py
Вспомогательные функции: хеширование паролей, валидация данных
"""

import hashlib
import re


def hash_password(password):
    """
    Хеширует пароль с помощью SHA-256

    Args:
        password (str): Пароль в открытом виде

    Returns:
        str: Хеш пароля
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """
    Проверяет соответствие пароля хешу

    Args:
        password (str): Пароль в открытом виде
        password_hash (str): Хеш пароля

    Returns:
        bool: True если пароль подходит
    """
    return hash_password(password) == password_hash


def validate_email(email):
    """
    Проверяет корректность email

    Args:
        email (str): Адрес электронной почты

    Returns:
        bool: True если email корректен
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username):
    """
    Проверяет корректность имени пользователя

    Args:
        username (str): Имя пользователя

    Returns:
        bool: True если имя корректно (только буквы, цифры, _)
    """
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


def validate_password(password):
    """
    Проверяет сложность пароля

    Args:
        password (str): Пароль

    Returns:
        bool: True если пароль соответствует требованиям
        str: Сообщение об ошибке
    """
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    if not any(c.isupper() for c in password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"
    if not any(c.islower() for c in password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"
    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    return True, "Пароль корректен"


def validate_phone(phone):
    """
    Проверяет корректность номера телефона

    Args:
        phone (str): Номер телефона

    Returns:
        bool: True если номер корректен
    """
    # Простая проверка: только цифры, +, -, пробелы, длина 10-15 символов
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, cleaned))