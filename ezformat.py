"""Simple formatting manager for markdown and other data"""
# (c) GitHub/puuhapake

import re

# If we really wanted, we could define some kind of
# transient procedural code, so that the users could --
# if they, for whatever reason, wanted to --
# include the string literal "__ESC!_DASH" in their posts.
def escape(content):
    """Temporarily replaces escaped characters with 
    unobtrusive placeholder strings.
    """
    content = content.replace("\\*", "__ESC!_ASTK")
    content = content.replace("\\-", "__ESC!_DASH")
    return content

def unescape(content):
    """Reverses the replacement done by :func:~ezformat.escape"""
    content = content.replace("__ESC!_ASTK", "*")
    content = content.replace("__ESC!_DASH", "-")
    return content

def set_dashes(content):
    """Replaces long dash sequences with proper HTML dashes"""
    content = content.replace("---", "&mdash;")
    content = content.replace("--", "&ndash;")
    return content

def set_emphs(content):
    """Manages asterisk-controlled md emphasis.
    Cannot handle nested asterisks!
    """
    content = re.sub(
        r"\*\*\*(.+?)\*\*\*", 
        r"<strong><em>\1</em></strong>", 
        content)
    content = re.sub(
        r"\*\*(.+?)\*\*",
        r"<strong>\1</strong>",
        content
    )
    content = re.sub(
        r"\*(.+?)\*", r"<em>\1</em>",
        content
    )
    return content

def to_emoticon(value):
    """Turns a numerical value to its corresponding emoticon"""
    match int(value):
        case 5:
            return ":D"
        case 4:
            return ":)"
        case 3:
            return ":/"
        case 2:
            return ":("
        case 1:
            return ":C"
        case _:
            return None
