import re

def escape(content):
    content = content.replace("\\*", "__ESC!_ASTK")
    content = content.replace("\\-", "__ESC!_DASH")
    return content

def unescape(content):
    content = content.replace("__ESC!_ASTK", "*")
    content = content.replace("__ESC!_DASH", "-")
    return content

def set_dashes(content):
    content = content.replace("---", "&mdash;")
    content = content.replace("--", "&ndash;")
    return content

def set_emphs(content):
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