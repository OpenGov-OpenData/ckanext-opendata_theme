# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckanext.opendata_theme.opengov_custom_footer.views as views


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()