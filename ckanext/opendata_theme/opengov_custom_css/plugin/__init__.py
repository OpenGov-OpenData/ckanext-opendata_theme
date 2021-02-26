import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import six
from ckan.exceptions import CkanVersionException

from ckanext.opendata_theme.opengov_custom_css.constants import CSS_METADATA, RAW_CSS

try:
    toolkit.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.opendata_theme.opengov_custom_css.plugin.pylons_plugin import MixinPlugin
else:
    from ckanext.opendata_theme.opengov_custom_css.plugin.flask_plugin import MixinPlugin


class Opendata_ThemePlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../static')
        toolkit.add_resource('../../base/fanstatic', 'opengov_custom_css_resource')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_css', 'Custom CSS')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom-css.custom_css', 'Custom CSS')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        schema.update({
            # This is a custom configuration option
            RAW_CSS: [ignore_missing, six.text_type],
            CSS_METADATA: [ignore_missing, dict],
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_custom_css': lambda x: None
        }
