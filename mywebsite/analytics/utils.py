import secrets

def create_analytics_reference(prefix=None):
    token = secrets.token_hex(10)
    if prefix is not None:
        return f'{prefix}{token}'
    return token
