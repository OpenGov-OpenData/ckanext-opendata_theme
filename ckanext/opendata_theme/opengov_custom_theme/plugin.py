import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.opendata_theme.base.helpers as helper


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'opendata_theme_group_alias': helper.get_group_alias,
            'opendata_theme_organization_alias': helper.get_organization_alias,
            'opendata_theme_get_default_extent': helper.get_default_extent,
            'version': helper.version_builder,
        }
