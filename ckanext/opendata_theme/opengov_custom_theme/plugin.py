from six import text_type

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.opendata_theme.base.helpers as helper
import ckanext.opendata_theme.opengov_custom_theme.blueprint as view


class OpenDataThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_not_sysadmin = toolkit.get_validator('ignore_not_sysadmin')

        schema.update({
            # This is a custom configuration option
            'contact_form_legend_content': [ignore_missing, ignore_not_sysadmin, text_type]
        })

        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'opendata_theme_group_alias': helper.get_group_alias,
            'opendata_theme_organization_alias': helper.get_organization_alias,
            'opendata_theme_get_default_extent': helper.get_default_extent,
            'opendata_theme_is_data_dict_active': helper.is_data_dict_active,
            'version': helper.version_builder,
        }

    # IBlueprint
    def get_blueprint(self):
        return view.get_blueprints()
