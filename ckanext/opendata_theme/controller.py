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

from ckanext.opendata_theme.constants import LAYOUTS
from ckanext.opendata_theme.processors import custom_style_processor, custom_naming_processor


class CustomCSSController(admin.AdminController):

    def custom_css(self):
        extra_vars = {}
        if request.method == 'POST':
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))

            custom_css, css_metadata = custom_style_processor.get_custom_css(data)
            contrast_errors = custom_style_processor.check_contrast()
            extra_vars.update({'errors': contrast_errors})
            if not contrast_errors:
                self.save_css_metadata(custom_css, css_metadata)
                css_metadata = self.sort_inputs_by_position(css_metadata)
                extra_vars.update(self.split_inputs_onto_two_columns(css_metadata))
                redirect_to(
                    controller='ckanext.opendata_theme.controller:CustomCSSController',
                    action='custom_css',
                    extra_vars=extra_vars
                )

        css_metadata = get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_css_metadata"})
        if not css_metadata:
            _, css_metadata = custom_style_processor.get_custom_css({})
            self.save_css_metadata({}, css_metadata)
        else:
            css_metadata = ast.literal_eval(css_metadata)
        css_metadata = self.sort_inputs_by_position(css_metadata)
        extra_vars.update(self.split_inputs_onto_two_columns(css_metadata))
        return render(
            'admin/custom_css.html',
            extra_vars=extra_vars
        )

    def reset_custom_css(self):
        extra_vars = {}
        _, css_metadata = custom_style_processor.get_custom_css({})
        self.save_css_metadata({}, css_metadata)
        css_metadata = self.sort_inputs_by_position(css_metadata)
        extra_vars.update(self.split_inputs_onto_two_columns(css_metadata))
        redirect_to(
            controller='ckanext.opendata_theme.controller:CustomCSSController',
            action='custom_css',
            extra_vars=extra_vars
        )

    def custom_home_page(self):
        extra_vars = {}
        if request.method == 'POST':
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))

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
                controller='ckanext.opendata_theme.controller:CustomCSSController',
                action='custom_home_page',
                extra_vars=extra_vars
            )
        # Get last or default custom naming
        custom_naming = get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_naming"})
        if not custom_naming:
            custom_naming = custom_naming_processor.get_custom_naming({})
            get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_naming": custom_naming})
        else:
            custom_naming = ast.literal_eval(custom_naming)
        custom_naming = self.sort_inputs_by_position(custom_naming)

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
        naming = self.sort_inputs_by_position(naming)
        extra_vars["custom_naming"] = naming
        redirect_to(
            controller='ckanext.opendata_theme.controller:CustomCSSController',
            action='custom_home_page',
            extra_vars=extra_vars
        )

    @staticmethod
    def save_css_metadata(custom_css, css_metadata):
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_raw_css": custom_css})
        get_action('config_option_update')({}, {"ckanext.opendata_theme.custom_css_metadata": css_metadata})

    @staticmethod
    def split_inputs_onto_two_columns(data):
        input_numbers = len(data)
        part_1 = OrderedDict(list(data.items())[0:input_numbers / 2])
        part_2 = OrderedDict(list(data.items())[input_numbers / 2:])
        return {"data_part_1": part_1, "data_part_2": part_2}

    @staticmethod
    def sort_inputs_by_position(css_metadata):
        list_for_sort = [(key, value) for key, value in css_metadata.items()]
        list_for_sort = sorted(list_for_sort, key=lambda x: x[1].get('position', 0))
        return OrderedDict(list_for_sort)
