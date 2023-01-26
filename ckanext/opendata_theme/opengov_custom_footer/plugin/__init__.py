import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.opengov_custom_footer.common_controller import CustomFooterCommonController
from ckanext.opendata_theme.opengov_custom_footer.constants import CONFIG_SECTION

if toolkit.check_ckan_version(min_version='2.9.0'):
    from ckanext.opendata_theme.opengov_custom_footer.plugin.flask_plugin import MixinPlugin
    from ckan.lib.helpers import literal
else:
    from ckanext.opendata_theme.opengov_custom_footer.plugin.pylons_plugin import MixinPlugin
    from webhelpers.html import literal


class OpenDataThemeFooterPlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../assets')
        toolkit.add_resource('../assets', 'opengov_custom_footer_resource')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_footer', 'Custom Footer')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom-footer.custom_footer', 'Custom Footer')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        schema.update({
            # This is a custom configuration option
            CONFIG_SECTION: [ignore_missing, dict],
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_footer_data': get_footer_data,
            'version': helper.version_builder,
        }


def get_footer_data(section):
    data = CustomFooterCommonController.get_custom_footer_metadata()
    return literal(data.get(section))
