# -*- coding: utf-8 -*-

import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.opendata_theme.opengov_custom_footer.common_controller import CustomFooterCommonController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


def custom_footer():
    return CustomFooterCommonController().custom_footer()


def reset_custom_footer():
    return CustomFooterCommonController().reset_custom_footer()


api = Blueprint('ckan-admin', __name__, url_prefix='/ckan-admin')
api.add_url_rule('/custom_footer/', methods=['GET', 'POST'], view_func=custom_footer)
api.add_url_rule('/reset_custom_footer/', methods=['POST'], view_func=reset_custom_footer)
