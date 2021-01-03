import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.exceptions import CkanVersionException

try:
    toolkit.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.opendata_theme.opengov_custom_footer.plugin.pylons_plugin import MixinPlugin
else:
    from ckanext.opendata_theme.opengov_custom_footer.plugin.flask_plugin import MixinPlugin
from webhelpers.html import literal
from ckanext.opendata_theme.opengov_custom_footer.controller import CustomFooterController
from ckanext.opendata_theme.opengov_custom_footer.constants import CONFIG_SECTION, CONTROLLER


class Opendata_ThemePlugin(MixinPlugin, plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    # plugins.implements(plugins.IValidators)

    # def get_validators(self):
    #     return {
    #         u'custom_header_url_validator': custom_header_url_validator,
    #     }

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../static')
        toolkit.add_resource('../../base/fanstatic', 'opengov_custom_theme_resource')
        toolkit.add_resource('../fanstatic', 'opengov_custom_footer_resource')

        if toolkit.check_ckan_version(min_version='2.4'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_footer', 'Custom Footer')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        # custom_header_url_validator = toolkit.get_validator('custom_header_url_validator')
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

    # IRoutes
    def before_map(self, m):
        '''
        Called before the routes map is generated.
        override all other mappings and returns the new map
        m.connect takes up to 5 parameters
        1.page template, 2.url route, 3.controller action, 4.controller class, 5. font-awesome icon class
        '''
        m.connect(
            'custom_footer',
            '/ckan-admin/custom_footer',
            action='custom_footer', controller=CONTROLLER, ckan_icon='paint-brush',
        )
        m.connect(
            'reset_custom_footer',
            '/ckan-admin/reset_custom_footer',
            action='reset_custom_footer', controller=CONTROLLER
        )
        return m


def get_footer_data(section):
    data = CustomFooterController.get_custom_footer_metadata()
    return literal(data.get(section))
