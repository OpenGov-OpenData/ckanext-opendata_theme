from six import text_type

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_not_sysadmin = toolkit.get_validator('ignore_not_sysadmin')
        url_validator = toolkit.get_validator('url_validator')

        schema.update({
            # This is a custom configuration option
            'governor_name': [ignore_missing, ignore_not_sysadmin, text_type],
            'governor_link': [ignore_missing, ignore_not_sysadmin, text_type, url_validator],
            'lieutenant_governor_name': [ignore_missing, ignore_not_sysadmin, text_type],
            'lieutenant_governor_link': [ignore_missing, ignore_not_sysadmin, text_type, url_validator]
        })

        return schema
