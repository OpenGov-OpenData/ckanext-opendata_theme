# -*- coding: utf-8 -*-

import ckan.controllers.admin as admin
import ckan.plugins as p

from ckanext.opendata_theme.opengov_custom_header.controller import CustomHeaderController
from ckanext.opendata_theme.opengov_custom_header.constants import CONTROLLER


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
            'custom_header',
            '/ckan-admin/custom_header',
            action='custom_header', controller=CONTROLLER, ckan_icon='paint-brush',
        )
        m.connect(
            'reset_custom_header',
            '/ckan-admin/reset_custom_header',
            action='reset_custom_header', controller=CONTROLLER
        )
        m.connect(
            'add_link_to_header',
            '/ckan-admin/add_link_to_header',
            action='add_link', controller=CONTROLLER
        )
        m.connect(
            'remove_link_from_header',
            '/ckan-admin/remove_link_from_header',
            action='remove_link', controller=CONTROLLER
        )
        return m
