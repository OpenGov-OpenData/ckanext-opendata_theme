# -*- coding: utf-8 -*-
import ckan.plugins as p


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes
    def before_map(self, m):
        '''
        Called before the routes map is generated.
        override all other mappings and returns the new map
        m.connect takes up to 5 parameters
        1.page template, 2.url route, 3.controller action, 4.controller class, 5. font-awesome icon class
        '''
        controller = 'ckanext.opendata_theme.opengov_custom_search_filter.controller:ResourceTypeController'
        m.connect(
            'resource_types',
            '/ckan-admin/resource_types',
            action='manage_resource_types', controller=controller, ckan_icon='filter',
        )
        m.connect(
            'reset_resource_types',
            '/ckan-admin/reset_resource_types',
            action='reset_resource_types', controller=controller
        )
        return m
