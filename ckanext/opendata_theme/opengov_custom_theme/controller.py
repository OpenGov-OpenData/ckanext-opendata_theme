import json

import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController


class ResourceTypeController(BaseCompatibilityController):
    def _check_sysadmin(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

    def manage_resource_types(self):
        self._check_sysadmin()

        categories = helper.get_resource_type_config()
        enabled = tk.asbool(tk.config.get(helper.RESOURCE_TYPE_FILTER_ENABLED_KEY) or False)
        categories_json = json.dumps(categories, indent=2)
        errors = {}

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            enabled = tk.asbool(data.get('enabled', False))
            categories_json = data.get('categories_json', '')
            try:
                parsed = helper.resource_type_categories_validator(categories_json)
                self.store_data(helper.RESOURCE_TYPE_CATEGORIES_KEY, parsed)
                context = {'model': model, 'user': tk.c.user}
                tk.get_action('config_option_update')(
                    context, {helper.RESOURCE_TYPE_FILTER_ENABLED_KEY: 'true' if enabled else 'false'}
                )
                categories_json = json.dumps(parsed, indent=2)
            except tk.Invalid as err:
                errors = {'categories_json': [str(err)]}

        return tk.render('admin/resource_types_form.html', extra_vars={
            'categories_json': categories_json,
            'enabled': enabled,
            'errors': errors,
        })

    def reset_resource_types(self):
        self._check_sysadmin()
        self.store_data(helper.RESOURCE_TYPE_CATEGORIES_KEY, helper.DEFAULT_RESOURCE_TYPE_CATEGORIES)
        return tk.redirect_to('resource_types.manage_resource_types')
