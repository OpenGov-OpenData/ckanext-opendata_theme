import re
import six
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.opengov_custom_css.controller import CustomCSSController
from ckanext.opendata_theme.opengov_custom_css.constants import CSS_METADATA, RAW_CSS

if toolkit.check_ckan_version(min_version='2.9.0'):
    from ckanext.opendata_theme.opengov_custom_css.plugin.flask_plugin import MixinPlugin
else:
    from ckanext.opendata_theme.opengov_custom_css.plugin.pylons_plugin import MixinPlugin


class OpenDataThemeCustomCSSPlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../assets')
        toolkit.add_resource('../assets', 'opengov_custom_css_resource')

        if toolkit.check_ckan_version(min_version='2.4', max_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom_css', 'Custom CSS', icon='file-code-o')
        elif toolkit.check_ckan_version(min_version='2.9'):
            toolkit.add_ckan_admin_tab(ckan_config, 'custom-css.custom_css', 'Custom CSS', icon='file-code-o')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        schema.update({
            RAW_CSS: [ignore_missing, six.text_type, custom_css_validator],
            CSS_METADATA: [ignore_missing, dict, css_meta_validator],
        })
        return schema

    # IValidators
    def get_validators(self):
        return {
            u'custom_css_validator': custom_css_validator,
            u'css_meta_validator': css_meta_validator,
        }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_custom_css': get_custom_raw_css,
            'version': helper.version_builder,
        }


def get_custom_raw_css():
    return CustomCSSController.get_raw_css()


def custom_css_validator(value):
    return value
    # remove all html from css is not working well as > is allowed css symbol
    # clear_value = helper.sanityze_all_html(value)
    # return clear_value


def css_meta_validator(css_meta):
    for title, color in css_meta.items():
        color_validator(color.get('value'))
    return css_meta


def color_validator(value):
    if not re.fullmatch('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
        raise toolkit.Invalid('Invalid color {}'.format(value))
    return value
