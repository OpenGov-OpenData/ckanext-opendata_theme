# encoding: utf-8
import json
import ast

import ckan.controllers.admin as admin
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.logic import (
    clean_dict,
    tuplize_dict,
    parse_params,
)
from ckan.plugins.toolkit import (
    render,
    request,
    get_action
)


from processor import custom_style_processor


class CustomCSSController(admin.AdminController):

    def custom_css(self):
        if request.method == 'POST':
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))

            dump_css = self.save_dump_css(data)

            return render('admin/custom_css.html', extra_vars={'data': dump_css})

        dump_css = get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_css_dump"})
        if not dump_css:
            dump_css = self.save_dump_css({})
        else:
            dump_css = ast.literal_eval(dump_css)
        return render('admin/custom_css.html', extra_vars={'data': dump_css})

    def save_dump_css(self, data):
        custom_css, dump_css = custom_style_processor.get_custom_css(data)
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_raw_css": custom_css})
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_css_dump": dump_css})
        return dump_css