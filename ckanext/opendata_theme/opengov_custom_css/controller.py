# encoding: utf-8
from collections import OrderedDict

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.plugins.toolkit import config, get_action, render, request, ValidationError

from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.opendata_theme.opengov_custom_css.processor import custom_style_processor
from ckanext.opendata_theme.opengov_custom_css.constants import (
    CSS_METADATA, RAW_CSS,
    ACCOUNT_HEADER_FIELDS, NAVIGATION_HEADER_FIELDS,
    MODULE_HEADER_FIELDS, FOOTER_FIELDS
)


class CustomCSSController(BaseCompatibilityController):
    redirect_to_action_kwargs = dict(endpoint='custom-css.custom_css')

    def custom_css(self):
        context = {'model': model, 'user': tk.c.user}
        css_metadata = self.get_data(CSS_METADATA)
        if not css_metadata:
            # This case can happen only during the cold start on empty DB.
            default_raw_css, css_metadata = custom_style_processor.get_custom_css({})
            self.save_css_metadata(default_raw_css, css_metadata)

        if request.method == 'POST':
            form_data = self.get_form_data(request)
            custom_css, css_metadata = custom_style_processor.get_custom_css(form_data)

            try:
                custom_style_processor.check_contrast()
                self.save_css_metadata(custom_css, css_metadata)

                get_action('config_option_update')(context,
                    {'ckan.site_custom_css': form_data.get('ckan.site_custom_css')}
                )
            except ValidationError as e:
                errors = e.error_dict
                extra_vars = {'data': form_data, 'errors': errors}
                extra_vars.update(self.get_form_fields(css_metadata))
                return render('admin/custom_css_form.html', extra_vars=extra_vars)

        site_custom_css = get_action('config_option_show')(context,
            {'key':'ckan.site_custom_css'}
        )

        data = {'ckan.site_custom_css': site_custom_css}
        extra_vars = {'data': data, 'errors': {}}
        extra_vars.update(self.get_form_fields(css_metadata))
        return render('admin/custom_css_form.html', extra_vars=extra_vars)

    def reset_custom_css(self):
        default_raw_css, default_css_metadata = custom_style_processor.get_custom_css({})
        self.save_css_metadata(default_raw_css, default_css_metadata)
        return self.redirect_to()

    def save_css_metadata(self, custom_css, css_metadata):
        self.store_data(RAW_CSS, custom_css)
        metadata = self.sort_inputs_by_title(css_metadata)
        self.store_data(CSS_METADATA, metadata)

    @staticmethod
    def get_raw_css():
        return get_action('config_option_show')({'ignore_auth': True}, {'key': RAW_CSS})

    @staticmethod
    def get_form_fields(css_metadata):
        account_header_fields = OrderedDict()
        navigation_header_fields = OrderedDict()
        module_header_fields = OrderedDict()
        link_fields = OrderedDict()
        footer_fields = OrderedDict()
        for key, value in css_metadata.items():
            if key in ACCOUNT_HEADER_FIELDS:
                account_header_fields[key] = value
            if key in NAVIGATION_HEADER_FIELDS:
                navigation_header_fields[key] = value
            if key in MODULE_HEADER_FIELDS:
                module_header_fields[key] = value
            if key in FOOTER_FIELDS:
                footer_fields[key] = value
        return {
            'account_header_fields': account_header_fields,
            'navigation_header_fields': navigation_header_fields,
            'module_header_fields': module_header_fields,
            'footer_fields': footer_fields
        }

    @staticmethod
    def sort_inputs_by_title(css_metadata):
        list_for_sort = [(key, value) for key, value in css_metadata.items()]
        list_for_sort = sorted(list_for_sort, key=lambda x: x[1].get('title', ''))
        return OrderedDict(list_for_sort)
