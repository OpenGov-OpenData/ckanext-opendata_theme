CONFIG_KEY = 'ckanext.opendata_theme.custom_footer.data'

CONTROLLER = 'ckanext.opendata_theme.opengov_custom_footer.plugin.pylons_plugin:CustomFooterController'

ALLOWED_HTML_TAGS = {
    'a', 'abbr', 'acronym', 'b', 'br', 'div', 'em',
    'i', 'img', 'li','ol', 'p', 'strong', 'ul'
}

ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'class', 'target', 'title'],
    'img': ['src', 'alt', 'class', 'height', 'style', 'width'],
}

ALLOWED_CSS_PROPERTIES = [
    'background-color', 'border-bottom-color', 'border-collapse',
    'border-color', 'border-left-color', 'border-right-color',
    'border-top-color', 'clear', 'color', 'cursor', 'direction', 'display',
    'float', 'font', 'font-family', 'font-size', 'font-style', 'font-variant',
    'font-weight', 'height', 'letter-spacing', 'line-height', 'overflow',
    'text-align', 'text-decoration', 'text-indent', 'vertical-align',
    'white-space', 'width'
]
