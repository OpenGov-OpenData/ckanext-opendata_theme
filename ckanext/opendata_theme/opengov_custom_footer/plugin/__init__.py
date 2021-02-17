import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.exceptions import CkanVersionException

try:
    toolkit.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.opendata_theme.opengov_custom_footer.plugin.pylons_plugin import MixinPlugin
    from webhelpers.html import literal
else:
    from ckanext.opendata_theme.opengov_custom_footer.plugin.flask_plugin import MixinPlugin
    from ckan.lib.helpers import literal
from ckanext.opendata_theme.opengov_custom_footer.common_controller import CustomFooterCommonController as CustomFooterController
from ckanext.opendata_theme.opengov_custom_footer.constants import CONFIG_SECTION


class Opendata_ThemePlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../static')
        toolkit.add_resource('../../base/fanstatic', 'opengov_custom_theme_resource')
        toolkit.add_resource('../fanstatic', 'opengov_custom_footer_resource')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_footer', 'Custom Footer')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'ckan-admin.custom_footer', 'Custom Footer')

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
        }


def get_footer_data(section):
    data = CustomFooterController.get_custom_footer_metadata()
    return literal(data.get(section))
