import re
from markupsafe import escape

def validate_email(email):
    if not email:
        return False, "Email is required"

    email = email.strip()

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, email

def validate_password(password):
    if not password:
        return False, "Password is required"

    if len(password) < 6 or not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
        return False, "Password must be at least 6 characters, contain an uppercase letter and a number"

    return True, password
