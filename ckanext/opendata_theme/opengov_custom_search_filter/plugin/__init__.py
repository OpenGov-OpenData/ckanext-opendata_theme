from six import text_type

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.opendata_theme.opengov_custom_search_filter.helpers as helper
from ckanext.opendata_theme.opengov_custom_search_filter.constants import (
    RESOURCE_TYPE_CATEGORIES_KEY,
    RESOURCE_TYPE_FILTER_ENABLED_KEY,
)

if toolkit.check_ckan_version(min_version='2.9.0'):
    from ckanext.opendata_theme.opengov_custom_search_filter.plugin.flask_plugin import MixinPlugin
else:
    from ckanext.opendata_theme.opengov_custom_search_filter.plugin.pylons_plugin import MixinPlugin


class OpenDataThemeSearchFilterPlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_ckan_admin_tab(
            ckan_config, 'resource_types.manage_resource_types', 'Resource Type Filter', icon='filter'
        )

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_not_sysadmin = toolkit.get_validator('ignore_not_sysadmin')

        schema.update({
            RESOURCE_TYPE_FILTER_ENABLED_KEY: [ignore_missing, ignore_not_sysadmin, text_type],
            RESOURCE_TYPE_CATEGORIES_KEY: [ignore_missing, helper.resource_type_categories_validator],
        })

        return schema

    # IPackageController
    def before_search(self, search_params):
        enabled = toolkit.asbool(toolkit.config.get(RESOURCE_TYPE_FILTER_ENABLED_KEY) or False)
        res_type = search_params.get('extras', {}).get('ext_res_type', '')
        if isinstance(res_type, list):
            res_type = res_type[0] if res_type else ''
        formats = helper.get_resource_type_formats().get(res_type) if (enabled and res_type) else None
        if formats:
            fq_parts = ['res_format:"{}"'.format(helper.escape_solr_value(f)) for f in formats]
            fq = '({})'.format(' OR '.join(fq_parts))
            existing_fq = search_params.get('fq', '')
            search_params['fq'] = (existing_fq + ' ' + fq).strip() if existing_fq else fq
        return search_params

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'opendata_theme_get_resource_type_categories': helper.get_resource_type_categories,
            'opendata_theme_get_active_res_type': helper.get_active_res_type,
        }
