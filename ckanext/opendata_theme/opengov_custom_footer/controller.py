# encoding: utf-8
import ast

import ckan.controllers.admin as admin
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.logic import (
    clean_dict,
    tuplize_dict,
    parse_params, ValidationError
)
from ckan.plugins.toolkit import (
    get_action,
    redirect_to,
    render,
    request
)

from ckanext.opendata_theme.opengov_custom_footer.constants import CONFIG_SECTION, CONTROLLER


class CustomFooterController(admin.AdminController):
    def custom_footer(self):
        custom_footer = self.get_custom_footer_metadata()
        if request.method == 'POST':
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))
            custom_footer = {
                'layout_type': int(data.get('layout_type', 1)),
                'content_0': data.get('content-0'),
                'content_1': data.get('content-1'),
                'content_2': data.get('content-2'),
                'content_3': data.get('content-3'),
            }
            error = self.save_footer_metadata(custom_footer)
            custom_footer['errors'] = error

        return render('admin/custom_footer.html',
                      extra_vars=dict(data=custom_footer))

    def redirect_to_custom_footer_page(self, vars):
        redirect_to(
            controller=CONTROLLER,
            action='custom_footer',
            extra_vars=vars
        )

    def reset_custom_footer(self):
        self.save_footer_metadata({})
        self.redirect_to_custom_footer_page({})

    @staticmethod
    def save_footer_metadata(custom_footer):
        try:
            CustomFooterController.store_data(CONFIG_SECTION, custom_footer)
        except ValidationError as ex:
            return ex.error_summary

    @staticmethod
    def get_custom_footer_metadata():
        data = CustomFooterController.get_data(CONFIG_SECTION)
        return data

    @staticmethod
    def store_data(config_key, data):
        get_action('config_option_update')({}, {config_key: data})

    @staticmethod
    def get_data(config_key):
        data = get_action('config_option_show')({}, {"key": config_key})
        if not data:
            return {}
        try:
            data_dict = ast.literal_eval(data)
        except ValueError:
            data_dict = data
        return data_dict
