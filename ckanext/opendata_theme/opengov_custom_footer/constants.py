CONFIG_SECTION = 'ckanext.opendata_theme.custom_footer.data'
CONTROLLER = 'ckanext.opendata_theme.opengov_custom_footer.plugin.pylons_plugin:CustomFooterController'
ALLOWED_HTML_TAGS = [
    'div', 'img', 'a', 'br', 'p', 'abbr',
    'acronym', 'b', 'em', 'i', 'li', 'ol',
    'strong', 'ul', 'href'
]
ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'img': ['src', 'alt', 'style'],
}
