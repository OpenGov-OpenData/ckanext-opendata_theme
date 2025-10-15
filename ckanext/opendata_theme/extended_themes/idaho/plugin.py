from six import text_type

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

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_not_sysadmin = toolkit.get_validator('ignore_not_sysadmin')

        schema.update({
            # Configuration option for filter fields
            'ckanext.custom_search.filter_fields': [ignore_missing, ignore_not_sysadmin, text_type]
        })

        return schema

    # IBlueprint
    def get_blueprint(self):
        return search_blueprint