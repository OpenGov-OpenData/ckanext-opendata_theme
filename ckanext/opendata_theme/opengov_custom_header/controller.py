# encoding: utf-8
import six
import ckan.plugins.toolkit as tk
from ckan import model

try:
    from webhelpers.html import literal
except ModuleNotFoundError:
    from ckan.lib.helpers import literal  # noqa: F401

import ckanext.opendata_theme.base.helpers as helper
from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION
from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController


class Link(object):
    def __init__(self, title, url, position, active=False):
        self.title = six.text_type(title)
        self.url = six.text_type(url)
        self.position = position
        self.active = active

    def __repr__(self):
        return '{}:{}'.format(self.position, self.title)

    def to_dict(self):
        return {
            'position': self.position,
            'title': self.title,
            'url': self.url
        }


class CustomHeaderController(BaseCompatibilityController):
    def custom_header(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        custom_header = self.get_custom_header_metadata()
        if not custom_header:
            # this block is required for base initialization
            # it happens only once when default custom header metadata is not set
            # because it is set in build_pages_nav_main helper function which is called
            # during the page rendering.
            # reset_custom_header is able to render the page in the background for setting default metadata.
            self.reset_custom_header()

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            custom_header = {
                'layout_type': data.get('layout_type', 'default'),
                'links': []
            }
            if isinstance(data.get('url'), list):
                for index in range(len(data.get('url'))):
                    custom_header['links'].append(
                        Link(
                            title=data['title'][index],
                            url=data['url'][index],
                            position=data['position'][index]
                        )
                    )
            else:
                custom_header['links'].append(
                    Link(
                        title=data['title'],
                        url=data['url'],
                        position=data['position']
                    )
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

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            header_data = self.get_custom_header_metadata()
            header_data.get('links', []).append(
                Link(
                    title=data.get('new_title'),
                    url=data.get('new_url'),
                    position=len(header_data.get('links', [])),
                ))
            error = self.save_custom_header_metadata(header_data)
            header_data['errors'] = error
            return tk.render('admin/custom_header_form.html',
                             extra_vars=header_data)
        return tk.redirect_to(custom_header_route)

    def remove_link(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            header_data = self.get_custom_header_metadata()
            item = [link for link in header_data['links'] if link.title == data['to_remove']]
            try:
                header_data['links'].remove(item[0])
                error = self.save_custom_header_metadata(header_data)
                header_data['errors'] = error
            except IndexError:
                header_data['errors'] = "Unable to remove link."
            return tk.render('admin/custom_header_form.html',
                             extra_vars=header_data)
        return tk.redirect_to(custom_header_route)

    def reset_custom_header(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'

        default_header = {
            'layout_type': 'default',
            'links': [
                {'position': 0, 'title': 'Datasets', 'url': '/dataset'},
                {'position': 1, 'title': helper.get_organization_alias(), 'url': '/organization/'},
                {'position': 2, 'title': helper.get_group_alias(), 'url': '/group/'},
                {'position': 3, 'title': 'About', 'url': '/about'}
            ]
        }
        self.save_custom_header_metadata(default_header)

        return tk.redirect_to(custom_header_route)

    def save_custom_header_metadata(self, custom_header):
        try:
            data_dict = custom_header.copy()
            links = []
            for item in custom_header.get('links', []):
                links.append(item.to_dict())
            data_dict['links'] = links
            BaseCompatibilityController.store_data(CONFIG_SECTION, data_dict)
        except tk.ValidationError as ex:
            return ex.error_summary

    def get_custom_header_metadata(self):
        data_dict = BaseCompatibilityController.get_data(CONFIG_SECTION)
        links = []
        for item in data_dict.get('links', []):
            if isinstance(item, dict):
                item = Link(**item)
            links.append(item)
        if links:
            data_dict['links'] = links
        return data_dict
