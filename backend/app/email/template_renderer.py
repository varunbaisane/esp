from pathlib import Path
# pyrefly: ignore [missing-import]
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.email.theme import theme

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_email(template_name: str, context: dict) -> str:
    """
    Renders a Jinja2 template with the given context and standard theme variables.
    """
    template = env.get_template(template_name)
    merged_context = {
        "theme": theme,
        **context
    }
    return template.render(**merged_context)
