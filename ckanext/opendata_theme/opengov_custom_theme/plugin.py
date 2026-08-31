from six import text_type

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.opendata_theme.base.helpers as helper
import ckanext.opendata_theme.opengov_custom_theme.blueprint as view


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')
        toolkit.add_resource('assets', 'opengov_custom_theme')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_not_sysadmin = toolkit.get_validator('ignore_not_sysadmin')

        schema.update({
            # This is a custom configuration option
            'contact_form_legend_content': [ignore_missing, ignore_not_sysadmin, text_type]
        })

        return schema

    # IPackageController
    def before_dataset_search(self, search_params):
        try:
            res_type = toolkit.request.params.get('res_type', '')
        except Exception:
            res_type = ''
        if res_type and res_type in helper.RESOURCE_TYPE_FORMATS:
            formats = helper.RESOURCE_TYPE_FORMATS[res_type]
            fq_parts = ['res_format:"{}"'.format(f) for f in formats]
            fq = '({})'.format(' OR '.join(fq_parts))
            existing_fq = search_params.get('fq', '')
            search_params['fq'] = (existing_fq + ' ' + fq).strip() if existing_fq else fq
        return search_params

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'opendata_theme_group_alias': helper.get_group_alias,
            'opendata_theme_organization_alias': helper.get_organization_alias,
            'opendata_theme_get_default_extent': helper.get_default_extent,
            'opendata_theme_get_footer_script_snippet': helper.get_footer_script_snippet,
            'opendata_theme_is_data_dict_active': helper.is_data_dict_active,
            'version': helper.version_builder,
            'opendata_theme_segment_writekey': helper.get_segment_writekey,
            'opendata_theme_platform_uuid': helper.get_user_uuid,
            'opendata_theme_entity': helper.get_entity_id,
            'opendata_theme_get_resource_type_categories': helper.get_resource_type_categories,
            'opendata_theme_get_active_res_type': helper.get_active_res_type,
        }

    # IBlueprint
    def get_blueprint(self):
        return view.get_blueprints()
