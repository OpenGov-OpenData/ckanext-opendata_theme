import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.opendata_theme.extended_themes.idaho.blueprint import search_blueprint


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')

    # IBlueprint
    def get_blueprint(self):
        return search_blueprint