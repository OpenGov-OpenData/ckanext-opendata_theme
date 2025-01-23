import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def get_arcgis_link(resources):
    for resource in resources:
        if resource.get('name') in ['ArcGIS Hub Dataset', 'ArcGIS Open Dataset'] \
                and resource.get('format') == 'HTML':
            return resource.get('url')
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
            'opendata_theme_get_arcgis_link': get_arcgis_link
        }
