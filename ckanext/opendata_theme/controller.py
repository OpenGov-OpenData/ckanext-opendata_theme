# encoding: utf-8
import json
import ast
from collections import OrderedDict

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

            custom_css, dump_css = custom_style_processor.get_custom_css(data)
            contrast_errors = custom_style_processor.check_contrast()
            if not contrast_errors:
                self.save_dump_css(custom_css, dump_css)
            extra_vars = {'errors': contrast_errors}
            extra_vars.update(self.split_inputs_onto_two_columns(dump_css))
            return render('admin/custom_css.html', extra_vars=extra_vars)

        dump_css = get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_css_dump"})
        if not dump_css:
            _, dump_css = custom_style_processor.get_custom_css({})
            self.save_dump_css({}, dump_css)
        else:
            dump_css = ast.literal_eval(dump_css)

        return render('admin/custom_css.html', extra_vars=self.split_inputs_onto_two_columns(dump_css))

    def save_dump_css(self, custom_css, dump_css):
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_raw_css": custom_css})
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_css_dump": dump_css})

    def split_inputs_onto_two_columns(self, data):
        input_numbers = len(data)
        part_1 = OrderedDict(data.items()[0:input_numbers / 2])
        part_2 = OrderedDict(data.items()[input_numbers / 2:])
        return {"data_part_1": part_1, "data_part_2": part_2}
