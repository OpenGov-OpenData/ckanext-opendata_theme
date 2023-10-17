import json
from logging import getLogger

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

log = getLogger(__name__)

boolean_validator = toolkit.get_validator('boolean_validator')


def display_org(organization_name):
    """Check if organization should be displayed"""
    try:
        result = toolkit.get_action('organization_show')(None, {'id': organization_name})
        extras = result.get('extras', {})
        for field in extras:
            if field.get('key', '').lower() in ['hide', 'hidden'] and boolean_validator(field.get('value'), None):
                return False
    except Exception:
        log.error('Error in retrieving metadata for organization %s', organization_name)
    return True


def get_org_upload_url(org_id=''):
    url_list = toolkit.config.get('ckanext.cnra_theme.upload_urls', '[]')
    urls = json.loads(url_list)
    for item in urls:
        if org_id == item.get('org_id'):
            return item.get('upload_url', '')
    return ''


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'opendata_theme_display_org': display_org,
            'opendata_theme_get_org_upload_url': get_org_upload_url
        }
