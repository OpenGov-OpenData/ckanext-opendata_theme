# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.opendata_theme.opengov_custom_homepage.common_controller import CustomCSSController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


api = Blueprint('custom-homepage', __name__, url_prefix='/ckan-admin')
api.add_url_rule('/custom_home_page/', methods=['GET', 'POST'], view_func=CustomCSSController().custom_home_page)
api.add_url_rule('/reset_custom_naming/', methods=['GET', 'POST'], view_func=CustomCSSController().reset_custom_naming)
