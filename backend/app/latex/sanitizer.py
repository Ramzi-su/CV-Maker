import re
from typing import Any, Dict, List, Union


LATEX_SPECIAL_CHARS = [
    (re.compile(r'\\'), r'\\textbackslash{}'),
    (re.compile(r'&'), r'\\&'),
    (re.compile(r'%'), r'\\%'),
    (re.compile(r'\$'), r'\\\$'),
    (re.compile(r'#'), r'\\#'),
    (re.compile(r'_'), r'\\_'),
    (re.compile(r'\{'), r'\\{'),
    (re.compile(r'\}'), r'\\}'),
    (re.compile(r'~'), r'\\textasciitilde{}'),
    (re.compile(r'\^'), r'\\textasciicircum{}'),
]

COMMON_REPLACEMENTS = [
    (re.compile(r'C\+\+'), r'C\\texttt{++}'),
    (re.compile(r'C#'), r'C\\#'),
    (re.compile(r'[“”"]'), "''"),
    (re.compile(r'[‘’\']'), "'"),
    (re.compile(r'[«»]'), "''"),
    (re.compile(r'…'), '...'),
    (re.compile(r'–|—'), '--'),
]


def escape_latex(text: Any) -> str:
    if text is None:
        return ""
    s = str(text)

    # Strip unwanted control characters (ASCII < 32 except newline, carriage return, tab)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)

    # First handle special replacements like C++ and C# before & or # are escaped
    for pattern, replacement in COMMON_REPLACEMENTS:
        s = pattern.sub(replacement, s)

    # Then escape LaTeX reserved syntax chars
    for pattern, replacement in LATEX_SPECIAL_CHARS:
        s = pattern.sub(replacement, s)

    return s


def sanitize_data(data: Any) -> Any:
    if isinstance(data, str):
        return escape_latex(data)
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: sanitize_data(value) for key, value in data.items()}
    elif hasattr(data, "model_dump"):
        return sanitize_data(data.model_dump())
    elif hasattr(data, "__dict__"):
        return sanitize_data(data.__dict__)
    return data
