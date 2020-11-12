# encoding: utf-8
import ast
from collections import OrderedDict

import ckan.controllers.admin as admin
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.logic import (
    clean_dict,
    tuplize_dict,
    parse_params
)
from ckan.plugins.toolkit import (
    get_action,
    redirect_to,
    render,
    request
)

from ckanext.opendata_theme.opengov_custom_homepage.constants import LAYOUTS
from ckanext.opendata_theme.opengov_custom_homepage.processor import custom_naming_processor


class CustomCSSController(admin.AdminController):
    def custom_home_page(self):
        if request.method == 'POST':
            data = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.POST))))
            self.store_config(data)
        # Get last or default custom naming
        custom_naming = get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_naming"})
        if not custom_naming:
            custom_naming = custom_naming_processor.get_custom_naming({})
            get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_naming": custom_naming})
        else:
            custom_naming = ast.literal_eval(custom_naming)
        custom_naming = self.sort_inputs_by_title(custom_naming)

        # Get last or default layout
        actual_layout = get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_homepage_style"})
        if not actual_layout:
            actual_layout = 1
        return render(
            'admin/custom_home_page.html',
            extra_vars={
                "home_page_layouts_list": LAYOUTS,
                "custom_naming": custom_naming,
                "actual_layout": actual_layout
            }
        )

    def reset_custom_naming(self):
        extra_vars = {}
        naming = custom_naming_processor.get_custom_naming({})
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_naming": naming})
        naming = self.sort_inputs_by_title(naming)
        extra_vars["custom_naming"] = naming
        redirect_to(
            controller='ckanext.opendata_theme.opengov_custom_homepage.controller:CustomCSSController',
            action='custom_home_page',
            extra_vars=extra_vars
        )

    @staticmethod
    def store_config(data):
        extra_vars = {}
        # Check and update home page layout style
        layout_style = data.get('custom_homepage_layout')
        if layout_style:
            get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_homepage_style": layout_style})
        extra_vars["actual_layout"] = layout_style

        # Parse and save naming
        naming = custom_naming_processor.get_custom_naming(data)
        extra_vars["custom_naming"] = naming
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_naming": naming})

        redirect_to(
            controller='ckanext.opendata_theme.opengov_custom_homepage.controller:CustomCSSController',
            action='custom_home_page',
            extra_vars=extra_vars
        )

    @staticmethod
    def sort_inputs_by_title(css_metadata):
        list_for_sort = [(key, value) for key, value in css_metadata.items()]
        list_for_sort = sorted(list_for_sort, key=lambda x: x[1].get('title', 0))
        return OrderedDict(list_for_sort)
