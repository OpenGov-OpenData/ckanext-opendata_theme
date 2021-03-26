import re
import string
from six.moves.urllib.parse import urlparse, quote

from ckan.exceptions import CkanVersionException
from ckan.logic.validators import Invalid
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config

from ckanext.opendata_theme.opengov_custom_header.controller import CustomHeaderController, Header
from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, DEFAULT_CONFIG_SECTION

try:
    toolkit.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.opendata_theme.opengov_custom_header.plugin.pylons_plugin import MixinPlugin
    from webhelpers.html import escape, literal

else:
    from ckanext.opendata_theme.opengov_custom_header.plugin.flask_plugin import MixinPlugin
    from ckan.lib.helpers import escape, literal

from ckanext.opendata_theme.base.template_helpers import version_builder


class Opendata_ThemePlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)

    def get_validators(self):
        return {
            u'custom_header_url_validator': custom_header_url_validator,
        }

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_header', 'Custom Header')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom-header.custom_header', 'Custom Header')

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
            'version': version_builder,
        }


def build_pages_nav_main(*args):
    controller = CustomHeaderController()
    default_metadata = controller.get_default_custom_header_metadata()
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
                    position=index
                ))
        else:
            from ckan.lib.helpers import build_nav_main
            base_links = build_nav_main(*args)
            expr = re.compile('(<li.*?</li>)', flags=re.DOTALL)
            default_header_links = expr.findall(base_links)
            parse_link = re.compile('href="(.*)">(.*?)</a>', flags=re.DOTALL)
            for index, link in enumerate(args):
                parsed_data = parse_link.findall(default_header_links[index])
                parsed_data = parsed_data[0] if len(parsed_data) == 1 else ((), ())
                data['links'].append(Header(
                    title=parsed_data[1],
                    link=parsed_data[0],
                    position=index,
                ))
        controller.save_default_header_metadata(data)

    custom_header = controller.get_custom_header_metadata()
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
