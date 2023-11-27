import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.opendata_theme.extended_themes.virginiaogda.helpers as vh


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
            'opendata_theme_get_featured_datasets': vh.get_featured_datasets,
            'opendata_theme_get_all_resource_count': vh.get_all_resource_count,
            'opendata_theme_get_contributors_count': vh.get_contributors_count,
        }
