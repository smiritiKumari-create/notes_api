"""
markdown_utils.py
-----------------
Converts raw Markdown to sanitised HTML.

Libraries used:
  • markdown  – converts Markdown → HTML
  • bleach    – sanitises the HTML to prevent XSS
"""

import markdown
import bleach
from bleach.css_sanitizer import CSSSanitizer

# Markdown extensions enabled
_EXTENSIONS = [
    "fenced_code",     # ``` code blocks
    "codehilite",      # syntax highlighting classes
    "tables",          # GFM tables
    "toc",             # [TOC] placeholder
    "nl2br",           # newline → <br>
    "attr_list",       # {: .class } attributes
    "footnotes",
]

# Tags & attributes allowed after sanitisation
_ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "pre", "code", "blockquote",
    "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td",
    "img", "hr", "br",
    "del", "ins", "sup", "sub",
    "details", "summary",
    "div", "span",
]

_ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "*":    ["class", "id"],
    "a":    ["href", "title", "rel"],
    "img":  ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "td":   ["align"],
    "th":   ["align"],
}

_css_sanitizer = CSSSanitizer(allowed_css_properties=["color", "background-color", "font-weight"])


def render_markdown(raw: str) -> str:
    """Convert raw Markdown string to sanitised HTML."""
    dirty_html = markdown.markdown(
        raw,
        extensions=_EXTENSIONS,
        extension_configs={
            "codehilite": {"guess_lang": False, "use_pygments": False},
        },
        output_format="html",
    )
    clean_html = bleach.clean(
        dirty_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        css_sanitizer=_css_sanitizer,
        strip=True,
    )
    return clean_html