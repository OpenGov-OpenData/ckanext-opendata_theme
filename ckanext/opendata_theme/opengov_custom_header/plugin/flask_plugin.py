# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.opendata_theme.opengov_custom_header.controller import CustomHeaderController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


api = Blueprint('custom-header', __name__, url_prefix='/ckan-admin')
api.add_url_rule('/custom_header/', methods=['GET', 'POST'],
                 view_func=CustomHeaderController().custom_header)
api.add_url_rule('/reset_custom_header/', methods=['GET', 'POST'],
                 view_func=CustomHeaderController().reset_custom_header)
api.add_url_rule('/add_link_to_header/', methods=['POST'],
                 view_func=CustomHeaderController().add_link)
api.add_url_rule('/remove_link_from_header/', methods=['POST'],
                 view_func=CustomHeaderController().remove_link)
