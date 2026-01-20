
def validate_name(name):
    if not name:
        return False, "Name is required"
    if len(name) < 2:
        return False, "Name is too short"
    return True, escape(name.strip())

def validate_email(email):
    if not email:
        return False, "Email is required"
    email = email.strip()
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        return False,"Invalid email format"
    return True, escape(email)

def validate_password(password):
    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, password

def validate_search(query):
    if not query:
        return False, ""
    if len(query) > 50:
        return False, "Search query too long"
    return True, escape(query.strip())
