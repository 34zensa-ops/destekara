import secrets
import string

def make_cid(name: str) -> str:
    suf = ''.join(secrets.choice(string.hexdigits.upper()) for _ in range(4))
    clean_name = ''.join(c for c in name if c.isalnum())[:20]
    return f"{clean_name}-{suf}"

def generate_secret(length=16):
    return secrets.token_urlsafe(length)
