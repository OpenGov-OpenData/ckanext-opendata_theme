# -*- coding: utf-8 -*-

import ckan.controllers.admin as admin
import ckan.plugins as p

from ckanext.opendata_theme.opengov_custom_homepage.common_controller import CustomCSSController
from ckanext.opendata_theme.opengov_custom_homepage.constants import CONTROLLER


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
            'custom_home_page',
            '/ckan-admin/custom_home_page',
            action='custom_home_page', controller=CONTROLLER
        )
        m.connect(
            'reset_custom_naming',
            '/ckan-admin/reset_custom_naming',
            action='reset_custom_naming', controller=CONTROLLER
        )
        return m


class CSSController(admin.AdminController, CustomCSSController):
    redirect_to_action_kwargs = dict(
        controller=CONTROLLER,
        action='custom_home_page',
    )
