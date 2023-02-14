# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.opendata_theme.opengov_custom_footer.common_controller import CustomFooterCommonController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return og_footer


og_footer = Blueprint('custom-footer', __name__, url_prefix='/ckan-admin')

og_footer.add_url_rule('/custom_footer/', methods=['GET', 'POST'],
                       view_func=CustomFooterCommonController().custom_footer)
og_footer.add_url_rule('/reset_custom_footer/', methods=['GET', 'POST'],
                       view_func=CustomFooterCommonController().reset_custom_footer)
