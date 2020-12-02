import re
import six
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import build_nav_main
from ckanext.opendata_theme.opengov_custom_header.controller import CustomHeaderController, Header
from webhelpers.html import escape, HTML, literal, url_escape

from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, CONTROLLER, DEFAULT_CONFIG_SECTION


class Opendata_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')
        toolkit.add_public_directory(ckan_config, 'static')
        toolkit.add_resource('../base/fanstatic', 'opengov_custom_theme_resource')
        toolkit.add_resource('../opengov_custom_header/fanstatic', 'opengov_custom_header_resource')

        if toolkit.check_ckan_version(min_version='2.4'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_header', 'Custom Header')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        schema.update({
            # This is a custom configuration option
            CONFIG_SECTION: [ignore_missing, dict],
            DEFAULT_CONFIG_SECTION: [ignore_missing, dict],
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'build_nav_main': build_pages_nav_main,
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
            'custom_header',
            '/ckan-admin/custom_header',
            action='custom_header', controller=CONTROLLER, ckan_icon='paint-brush',
        )
        m.connect(
            'reset_custom_header',
            '/ckan-admin/reset_custom_header',
            action='reset_custom_header', controller=CONTROLLER
        )
        m.connect(
            'add_link_to_header',
            '/ckan-admin/add_link_to_header',
            action='add_link', controller=CONTROLLER
        )
        m.connect(
            'remove_link_from_header',
            '/ckan-admin/remove_link_from_header',
            action='remove_link', controller=CONTROLLER
        )
        return m


def build_pages_nav_main(*args):
    default_metadata = CustomHeaderController.get_default_custom_header_metadata()
    if not default_metadata.get('links'):
        base_links = build_nav_main(*args)
        expr = re.compile('(<li.*?</li>)', flags=re.DOTALL)
        default_header_links = expr.findall(base_links)
        data = {'links': []}
        for index, link in enumerate(args):
            data['links'].append(Header(
                title=link[1],
                link=link[0],
                position=index,
                html=default_header_links[index]
            ))
        CustomHeaderController.save_default_header_metadata(data)

    custom_header = CustomHeaderController.get_custom_header_metadata()
    final_header_links = [item for item in custom_header.get('links', [])]

    final_header_links.sort(key=lambda x: x.position)
    return literal(''.join([item.html for item in final_header_links]))
