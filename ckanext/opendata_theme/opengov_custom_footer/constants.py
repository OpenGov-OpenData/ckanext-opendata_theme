CONFIG_SECTION = 'ckanext.opendata_theme.custom_footer.data'
CONTROLLER = 'ckanext.opendata_theme.opengov_custom_footer.controller:CustomFooterController'
ALLOWED_HTML_TAGS = [
    'div', 'img', 'a', 'br', 'p', 'abbr',
    'acronym', 'b', 'em', 'i', 'li', 'ol',
    'strong', 'ul'
]
ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'img': ['src', 'alt', 'style'],
}
