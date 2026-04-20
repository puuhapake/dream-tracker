"""Manages global app configurations."""

from secrets import token_hex
from pathlib import Path

MAX_TITLE_LENGTH = 35
MAX_DREAM_LENGTH = 900
MAX_USERNAME_LENGTH = 22
USERNAME_RESTRICTION = "[a-zA-Z0-9]+"
MIN_PASSWORD_LENGTH = 1
MAX_PREVIEW_LENGTH = 165
POST_LIMIT = 20

ERRORS = {
    "login": "Du måste vara inloggad.",
    "auth": "Fel användarnamn eller lösenord.",
    "nouser": "Användarnamnet hittades ej.",
    "userunavail": "Användarnamnet kan inte användas.",
    "mispatchpw": "Lösenorden stämmer inte överens.",
    "lenpw": "Lösenordet är för kort.",
    "userspec": ("Användarnamnet får inte innehålla"
                " specialtecken eller mellanslag."),
    "lenuser": "Användarnamnet är för långt.",
    "lenbody": "Texten är för lång.",
    "lentitle": "Titeln har fel längd.",
    "nopost": "Inlägget hittades inte.",
    "lencomm": "Kommentarets längd är fel.",
    "liked": "Inlägget har redan gillats!",
    "unavail": "Inlägget är inte tillgängligt.",
}

WORKING_DIR = Path(__file__).parent
CONFIG_PATH = WORKING_DIR / "config"
KEY_PATH = CONFIG_PATH / ".secret_key"

def get_session_key():
    """Retrieves a secret session key file if it exists, 
    or creates a new one otherwise.
    """
    CONFIG_PATH.mkdir(parents=True, exist_ok=True)

    if KEY_PATH.exists():
        session_key = KEY_PATH.read_text()
        return session_key
    else:
        key = token_hex(24)
        KEY_PATH.write_text(key)
        session_key = key
        return session_key

def csrf_token():
    """Creates a random hex string with 24 random bytes."""
    return token_hex(24)

def init():
    """Initializes server-side configurations."""
    get_session_key()
