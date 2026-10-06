# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.opendata_theme.opengov_custom_search_filter.controller import ResourceTypeController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return resource_types


resource_types = Blueprint('resource_types', __name__, url_prefix='/ckan-admin')

resource_types.add_url_rule('/resource_types', methods=['GET', 'POST'],
                            view_func=ResourceTypeController().manage_resource_types)
resource_types.add_url_rule('/reset_resource_types', methods=['POST'],
                            view_func=ResourceTypeController().reset_resource_types)
