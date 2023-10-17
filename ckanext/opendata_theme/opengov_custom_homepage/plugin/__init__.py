import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.opengov_custom_homepage.constants import CUSTOM_NAMING, CUSTOM_STYLE

if toolkit.check_ckan_version(min_version='2.9.0'):
    from ckanext.opendata_theme.opengov_custom_homepage.plugin.flask_plugin import MixinPlugin
else:
    from ckanext.opendata_theme.opengov_custom_homepage.plugin.pylons_plugin import MixinPlugin


class OpenDataThemeHomepagePlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../public')
        toolkit.add_resource('../assets', 'opengov_custom_homepage')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_homepage', 'Homepage', icon='file-code-o')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom-homepage.custom_homepage', 'Homepage', icon='file-code-o')

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
            'opendata_theme_get_story_banner': helper.get_story_banner,
            'opendata_theme_get_showcases_story': helper.showcase_story,
            'opendata_theme_get_value_from_extras': helper.get_value_from_extras,
            'opendata_theme_get_groups': helper.groups,
            'opendata_theme_get_datasets_new': helper.new_datasets,
            'opendata_theme_get_datasets_popular': helper.popular_datasets,
            'opendata_theme_get_datasets_recent': helper.recent_datasets,
            'opendata_theme_get_package_tracking_summary': helper.package_tracking_summary,
            'opendata_theme_get_custom_name': helper.get_custom_name,
            'opendata_theme_get_data': helper.get_data,
            'opendata_theme_custom_page_exists': helper.custom_page_exists,
            'version': helper.version_builder,
        }
