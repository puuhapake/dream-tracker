from secrets import token_hex
from pathlib import Path

session_key = None

WORKING_DIR = Path(__file__).parent
KEY_PATH = WORKING_DIR / "config" / ".secret_key"

def get_session_key():
    """Retrieves a secret session key file if it exists, 
    or creates a new one otherwise.
    """
    global session_key
    if KEY_PATH.exists():
        session_key = KEY_PATH.read_text()
    else:
        key = token_hex(24)
        KEY_PATH.write_text(key)
        session_key = key

def init():
    """Initializes server-side configurations."""
    get_session_key()