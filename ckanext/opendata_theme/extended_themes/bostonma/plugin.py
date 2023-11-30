import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.opendata_theme.base.helpers as helper


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('assets', 'bostonma_theme_resource')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'opendata_theme_abbreviate_name': helper.abbreviate_name
        }
