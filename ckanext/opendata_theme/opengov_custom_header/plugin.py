import re
import six
import string

from ckan.logic.validators import Invalid
from six.moves.urllib.parse import urlparse, quote
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config
from ckanext.opendata_theme.opengov_custom_header.controller import CustomHeaderController, Header
from webhelpers.html import escape, HTML, literal, url_escape

from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, CONTROLLER, DEFAULT_CONFIG_SECTION


class Opendata_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IValidators)

    def get_validators(self):
        return {
            u'custom_header_url_validator': custom_header_url_validator,
        }
    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')
        toolkit.add_public_directory(ckan_config, 'static')
        toolkit.add_resource('../base/fanstatic', 'opengov_custom_theme_resource')

        if toolkit.check_ckan_version(min_version='2.4'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_header', 'Custom Header')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        custom_header_url_validator = toolkit.get_validator('custom_header_url_validator')
        schema.update({
            # This is a custom configuration option
            CONFIG_SECTION: [ignore_missing, custom_header_url_validator],
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
        plugins = config.get('ckan.plugins', '').split(' ')
        data = {'links': []}
        if 'pages' in plugins:
            from ckanext.pages.plugin import build_pages_nav_main
            output = build_pages_nav_main(*args)
            expr = re.compile('(<li><a href="(.*?)">(.*?)</a></li>)', flags=re.DOTALL)
            default_header_links = expr.findall(output)
            for index, link in enumerate(default_header_links):
                data['links'].append(Header(
                    title=link[2],
                    link=link[1],
                    position=index,
                    html=link[0]
                ))
        else:
            from ckan.lib.helpers import build_nav_main
            base_links = build_nav_main(*args)
            expr = re.compile('(<li.*?</li>)', flags=re.DOTALL)
            default_header_links = expr.findall(base_links)

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

    final_header_links.sort(key=lambda x: int(x.position))
    return literal(''.join([item.html for item in final_header_links]))


def custom_header_url_validator(value):
    def check_characters(value):
        if set(value) <= set(string.ascii_letters + string.digits + '-./'):
            return False
        return True
    for item in value.get('links', []):
        link = item.get('link', '')
        if len(link) > 2000:
            raise Invalid('Url is too long. Only 2000 characters allowed for "{}"'.format(link))
        pieces = urlparse(link)
        if pieces.scheme and pieces.scheme != 'https':
            raise Invalid('Only HTTPS urls supported "{}"'.format(link))
        elif not pieces.path and not all([pieces.scheme, pieces.netloc]):
            raise Invalid('Empty relative path in relative url {}'.format(link))
        elif pieces.path and not all([pieces.scheme, pieces.netloc]) and check_characters(pieces.path):
            raise Invalid('Relative path contains invalid characters {}'.format(link))
        elif pieces.netloc and check_characters(pieces.netloc):
            raise Invalid('Url contains invalid characters "{}"'.format(link))
    return value
