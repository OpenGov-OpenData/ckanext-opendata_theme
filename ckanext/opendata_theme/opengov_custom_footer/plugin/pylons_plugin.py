# -*- coding: utf-8 -*-

import ckan.plugins as p

from ckanext.opendata_theme.opengov_custom_footer.constants import CONTROLLER


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
        m.connect(
            'custom_footer',
            '/ckan-admin/custom_footer',
            action='custom_footer', controller=CONTROLLER, ckan_icon='paint-brush',
        )
        m.connect(
            'reset_custom_footer',
            '/ckan-admin/reset_custom_footer',
            action='reset_custom_footer', controller=CONTROLLER
        )
        return m