import ast

import ckan.lib.navl.dictization_functions as dict_fns
from ckan.logic import (
    clean_dict, tuplize_dict, parse_params
)
from ckan.plugins.toolkit import get_action, redirect_to


class BaseCompatibilityController:
    redirect_to_action_kwargs = {}

    @staticmethod
    def get_form_data(request):
        try:
            # CKAN >= 2.9
            form_data = request.form
        except AttributeError:
            # CKAN < 2.9
            form_data = request.POST
        data = clean_dict(
            dict_fns.unflatten(
                tuplize_dict(
                    parse_params(form_data)
                )
            )
        )
        return data

    def redirect_to(self, extra_vars={}):
        return redirect_to(extra_vars=extra_vars, **self.redirect_to_action_kwargs)

    @staticmethod
    def store_data(config_key, data):
        get_action('config_option_update')({}, {config_key: data})

    @staticmethod
    def get_data(config_key):
        data = get_action('config_option_show')({'ignore_auth': True}, {"key": config_key})
        if not data:
            return {}
        try:
            data_dict = ast.literal_eval(data)
        except ValueError:
            data_dict = data
        return data_dict
