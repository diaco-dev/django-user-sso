TRANSLATIONS = {
    "Token is invalid or expired": "توکن نامعتبر است یا منقضی شده است",
    "Validation error": "خطای اعتبارسنجی",
    "Internal server error": "خطای داخلی سرور",
    "An unexpected error occurred": "یک خطای غیرمنتظره رخ داد",
    "This account does not exist.": "کاربر وجود ندارد"
}


def translate(message: str) -> str:
    return TRANSLATIONS.get(message, message)
