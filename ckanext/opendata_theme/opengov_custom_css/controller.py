# encoding: utf-8
from collections import OrderedDict
from ckan.plugins.toolkit import render, request

from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.opendata_theme.opengov_custom_css.processor import custom_style_processor
from ckanext.opendata_theme.opengov_custom_css.constants import CSS_METADATA, RAW_CSS


class CustomCSSController(BaseCompatibilityController):
    redirect_to_action_kwargs = dict(endpoint='custom-css.custom_css')

    def custom_css(self):
        extra_vars = {}
        if request.method == 'POST':
            data = self.get_form_data(request)
            extra_vars = self.store_config(data)

        css_metadata = self.get_data(CSS_METADATA)

        if not css_metadata:
            _, css_metadata = custom_style_processor.get_custom_css({})
            self.save_css_metadata({}, css_metadata)
        css_metadata = self.sort_inputs_by_title(css_metadata)
        extra_vars.update(self.split_inputs_onto_two_columns(css_metadata))
        return render('admin/custom_css.html', extra_vars=extra_vars)

    def reset_custom_css(self):
        extra_vars = {}
        _, css_metadata = custom_style_processor.get_custom_css({})
        self.save_css_metadata({}, css_metadata)
        css_metadata = self.sort_inputs_by_title(css_metadata)
        extra_vars.update(self.split_inputs_onto_two_columns(css_metadata))
        return self.redirect_to(extra_vars=extra_vars)

    def store_config(self, data):
        extra_vars = {}
        custom_css, css_metadata = custom_style_processor.get_custom_css(data)
        contrast_errors = custom_style_processor.check_contrast()
        extra_vars.update({'errors': contrast_errors})
        if not contrast_errors:
            self.save_css_metadata(custom_css, css_metadata)
            css_metadata = self.sort_inputs_by_title(css_metadata)
            extra_vars.update(self.split_inputs_onto_two_columns(css_metadata))
            self.redirect_to(extra_vars=extra_vars)
        return extra_vars

    def save_css_metadata(self, custom_css, css_metadata):
        self.store_data(RAW_CSS, custom_css)
        self.store_data(CSS_METADATA, css_metadata)

    @staticmethod
    def split_inputs_onto_two_columns(data):
        input_numbers = len(data)
        part_1 = OrderedDict(list(data.items())[0:int(round(input_numbers / 2))])
        part_2 = OrderedDict(list(data.items())[int(round(input_numbers / 2)):])
        return {"data_part_1": part_1, "data_part_2": part_2}

    @staticmethod
    def sort_inputs_by_title(css_metadata):
        list_for_sort = [(key, value) for key, value in css_metadata.items()]
        list_for_sort = sorted(list_for_sort, key=lambda x: x[1].get('title', ''))
        return OrderedDict(list_for_sort)
