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
        controller = 'ckanext.opendata_theme.opengov_custom_header.controller:CustomHeaderController'
        m.connect(
            'custom_header',
            '/ckan-admin/custom_header',
            action='custom_header', controller=controller, ckan_icon='paint-brush',
        )
        m.connect(
            'reset_custom_header',
            '/ckan-admin/reset_custom_header',
            action='reset_custom_header', controller=controller
        )
        return m
