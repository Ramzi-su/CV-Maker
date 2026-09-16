import os
from jinja2 import Environment, FileSystemLoader
from .sanitizer import escape_latex, sanitize_data

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def get_latex_jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    env.filters["latex"] = escape_latex
    return env


def render_latex(template_name: str, context: dict) -> str:
    env = get_latex_jinja_env()
    template = env.get_template(template_name)
    sanitized_context = sanitize_data(context)
    return template.render(**sanitized_context)
