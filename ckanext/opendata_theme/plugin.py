import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.opendata_theme.controller import CustomCSSController


class Opendata_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')
        toolkit.add_public_directory(ckan_config, 'static')
        toolkit.add_resource('fanstatic', 'opendata_theme_resource')

        if toolkit.check_ckan_version(min_version='2.4'):
             toolkit.add_ckan_admin_tab(ckan_config, 'custom_css', 'Custom CSS')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        schema.update({
            # This is a custom configuration option
            'ckanext.opendata_theme.custom_raw_css': [ignore_missing, unicode],
            'ckanext.opendata_theme.custom_css_metadata': [ignore_missing, dict]
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_custom_css': lambda x: None
        }

    # IRoutes
    def before_map(self, m):
        '''
        Called before the routes map is generated.
        override all other mappings and returns the new map
        m.connect takes up to 5 parameters
        1.page template, 2.url route, 3.controller action, 4.controller class, 5. font-awesome icon class
        '''
        ctrl = 'ckanext.opendata_theme.controller:CustomCSSController'
        m.connect(
            'custom_css',
            '/ckan-admin/custom_css',
            action='custom_css', controller=ctrl, ckan_icon='paint-brush',
        )
        m.connect(
            'reset_custom_css',
            '/ckan-admin/reset_custom_css',
            action='reset_custom_css', controller=ctrl
        )
        return m
