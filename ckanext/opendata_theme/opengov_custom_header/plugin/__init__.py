import re
import string
from six.moves.urllib.parse import urlparse

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.opengov_custom_header.controller import CustomHeaderController, Link
from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, DEFAULT_CONFIG_SECTION

try:
    from html import escape as html_escape
except ImportError:
    from cgi import escape as html_escape  # noqa: F401

if tk.check_ckan_version(min_version='2.9.0'):
    from ckanext.opendata_theme.opengov_custom_header.plugin.flask_plugin import MixinPlugin
    from ckan.lib.helpers import literal
else:
    from ckanext.opendata_theme.opengov_custom_header.plugin.pylons_plugin import MixinPlugin  # noqa: F401
    from webhelpers.html import literal  # noqa: F401


class OpenDataThemeHeaderPlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)

    # IConfigurer
    def update_config(self, ckan_config):
        tk.add_template_directory(ckan_config, '../templates')

        if tk.check_ckan_version(min_version='2.4', max_version='2.9'):
            tk.add_ckan_admin_tab(ckan_config, 'custom_header', 'Header Layout')
        elif tk.check_ckan_version(min_version='2.9'):
            tk.add_ckan_admin_tab(ckan_config, 'custom-header.custom_header', 'Header Layout')

    def update_config_schema(self, schema):
        ignore_missing = tk.get_validator('ignore_missing')
        schema.update({
            # This is a custom configuration option
            CONFIG_SECTION: [ignore_missing, custom_header_url_validator],
            DEFAULT_CONFIG_SECTION: [ignore_missing, dict],
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'opendata_theme_build_nav_main': build_nav_main,
            'opendata_theme_get_header_layout': get_header_layout,
            'opendata_theme_group_alias': helper.get_group_alias,
            'opendata_theme_organization_alias': helper.get_organization_alias,
            'version': helper.version_builder,
        }

    # IValidators
    def get_validators(self):
        return {
            u'custom_header_url_validator': custom_header_url_validator,
        }


def build_nav_main(*args):
    controller = CustomHeaderController()
    default_metadata = controller.get_default_custom_header_metadata()
    try:
        context = {'model': model, 'user': tk.c.user}
        tk.check_access('sysadmin', context, {})
        if not default_metadata.get('links'):
            data = {
                'layout_type': 'default',
                'links': []
            }
            try:
                from ckanext.pages.plugin import build_pages_nav_main
                output = build_pages_nav_main(*args)
            except Exception:
                from ckan.lib.helpers import build_nav_main
                output = build_nav_main(*args)
            expr = re.compile('(<li><a href="(.*?)">(.*?)</a></li>)', flags=re.DOTALL)
            header_links = expr.findall(output)
            for index, link in enumerate(header_links):
                data['links'].append(
                    Link(
                        title=link[2],
                        url=link[1],
                        position=index
                    )
                )
            controller.save_default_header_metadata(data)
    except tk.NotAuthorized:
        pass

    nav_output = ''
    custom_header = controller.get_custom_header_metadata()
    final_header_links = [item for item in custom_header.get('links', [])]
    final_header_links.sort(key=lambda x: int(x.position))
    for nav_link in final_header_links:
        title = html_escape(nav_link.title)
        link = tk.literal(u'<a href="{}">{}</a>'.format(nav_link.url, title))
        li = tk.literal('<li>') + link + tk.literal('</li>')
        nav_output = nav_output + li
    return nav_output


def get_header_layout():
    controller = CustomHeaderController()
    custom_header = controller.get_custom_header_metadata()
    layout_type = custom_header.get('layout_type', 'default')
    return layout_type


def custom_header_url_validator(value):
    def check_characters(value):
        if set(value) <= set(string.ascii_letters + string.digits + '-./'):
            return False
        return True
    for item in value.get('links', []):
        url = item.get('url', '')
        if len(url) > 2000:
            raise tk.Invalid('URL is too long. Only 2000 characters allowed for "{}"'.format(url))
        pieces = urlparse(url)
        if pieces.scheme and pieces.scheme != 'https':
            raise tk.Invalid('Only HTTPS URLs supported "{}"'.format(url))
        elif not pieces.path and not all([pieces.scheme, pieces.netloc]):
            raise tk.Invalid('Empty relative path in relative url {}'.format(url))
        elif pieces.path and not all([pieces.scheme, pieces.netloc]) and check_characters(pieces.path):
            raise tk.Invalid('Relative path contains invalid characters {}'.format(url))
        elif pieces.netloc and check_characters(pieces.netloc):
            raise tk.Invalid('URL contains invalid characters "{}"'.format(url))
    return value
