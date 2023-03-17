# encoding: utf-8
import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION
from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController


class CustomHeaderController(BaseCompatibilityController):
    default_header = {
        'layout_type': 'default',
        'links': [
            {'position': 0, 'title': 'Datasets', 'url': '/dataset'},
            {'position': 1, 'title': '{}s'.format(helper.get_organization_alias()), 'url': '/organization'},
            {'position': 2, 'title': '{}s'.format(helper.get_group_alias()), 'url': '/group'},
            {'position': 3, 'title': 'About', 'url': '/about'}
        ]
    }

    def custom_header(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        custom_header = self.get_custom_header_metadata()

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            custom_header = {
                'layout_type': data.get('layout_type', 'default'),
                'links': []
            }
            if isinstance(data.get('url'), list):
                for index in range(len(data.get('url'))):
                    custom_header['links'].append(
                        {
                            'position': data['position'][index],
                            'title': data['title'][index],
                            'url': data['url'][index]
                        }
                    )
            else:
                custom_header['links'].append(
                    {
                        'position': data['position'],
                        'title': data['title'],
                        'url': data['url']
                    }
                )
            error = self.save_custom_header_metadata(custom_header)
            custom_header['errors'] = error
        return tk.render('admin/custom_header_form.html',
                         extra_vars=custom_header)

    def add_link(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            header_data = self.get_custom_header_metadata()
            header_data.get('links', []).append(
                {
                    'position': len(header_data.get('links', [])),
                    'title': data.get('new_title'),
                    'url': data.get('new_url')
                }
            )
            error = self.save_custom_header_metadata(header_data)
            header_data['errors'] = error
            return tk.render('admin/custom_header_form.html',
                             extra_vars=header_data)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'
        return tk.redirect_to(custom_header_route)

    def remove_link(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            header_data = self.get_custom_header_metadata()
            item = [link for link in header_data['links'] if link.get('title') == data['to_remove']]
            try:
                header_data['links'].remove(item[0])
                error = self.save_custom_header_metadata(header_data)
                header_data['errors'] = error
            except IndexError:
                header_data['errors'] = "Unable to remove link."
            return tk.render('admin/custom_header_form.html',
                             extra_vars=header_data)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'
        return tk.redirect_to(custom_header_route)

    def reset_custom_header(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        self.save_custom_header_metadata(CustomHeaderController.default_header)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'
        return tk.redirect_to(custom_header_route)

    def save_custom_header_metadata(self, custom_header):
        try:
            CustomHeaderController.store_data(CONFIG_SECTION, custom_header)
        except tk.ValidationError as ex:
            return ex.error_summary

    def get_custom_header_metadata(self):
        data_dict = CustomHeaderController.get_data(CONFIG_SECTION)
        if not data_dict:
            data_dict = CustomHeaderController.default_header.copy()
        return data_dict
