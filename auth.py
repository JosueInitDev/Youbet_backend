import secrets

def generate_token():
    return secrets.token_hex(32)

def generate_username():
    return f"user_{secrets.token_hex(4)}"
