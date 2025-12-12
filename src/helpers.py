from flask_sqlalchemy import SQLAlchemy
from models import User
from urllib.parse import urlparse


def user_exists(db: SQLAlchemy, email: str) -> User | None:
    """returns the user if the user exists in the db"""
    check = db.session.execute(db.select(User).where(User.email == email)).scalar()
    return check


def is_safe(url: str) -> bool:
    """
    checks if url is relative for redirect
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        return not parsed.scheme and not parsed.netloc
    except ValueError:
        return False
