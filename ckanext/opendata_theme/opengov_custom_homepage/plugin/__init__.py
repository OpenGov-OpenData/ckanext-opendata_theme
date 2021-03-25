import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.exceptions import CkanVersionException

import ckanext.opendata_theme.opengov_custom_homepage.helpers as helper
from ckanext.opendata_theme.opengov_custom_homepage.constants import CUSTOM_NAMING, CUSTOM_STYLE

try:
    toolkit.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.opendata_theme.opengov_custom_homepage.plugin.pylons_plugin import MixinPlugin
else:
    from ckanext.opendata_theme.opengov_custom_homepage.plugin.flask_plugin import MixinPlugin
from ckanext.opendata_theme.base.template_helpers import version_builder


class Opendata_ThemePlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_home_page', 'Home Page Layout')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom-homepage.custom_home_page', 'Home Page Layout')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        schema.update({
            # This is a custom configuration option
            CUSTOM_NAMING: [ignore_missing, dict],
            CUSTOM_STYLE: [ignore_missing, int]
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'opendata_theme_get_dataset_count': helper.dataset_count,
            'opendata_theme_get_showcases': helper.showcases,
            'opendata_theme_get_groups': helper.groups,
            'opendata_theme_get_datasets_new': helper.new_datasets,
            'opendata_theme_get_datasets_popular': helper.popular_datasets,
            'opendata_theme_get_datasets_recent': helper.recent_datasets,
            'opendata_theme_get_package_metadata': helper.get_package_metadata,
            'opendata_theme_get_custom_name': helper.get_custom_name,
            'opendata_theme_get_data': helper.get_data,
            'version': version_builder,
        }
