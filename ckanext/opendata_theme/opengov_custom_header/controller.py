# encoding: utf-8
import six
import ckan.plugins.toolkit as tk
from ckan import model

try:
    from webhelpers.html import literal
except ModuleNotFoundError:
    from ckan.lib.helpers import literal

from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, DEFAULT_CONFIG_SECTION
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
            'title': self.title,
            'url': self.url,
            'position': self.position,
            'active': self.active,
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
                'links': [],
                'layout_type': data.get('layout_type', 'default')
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
            error = self.save_header_metadata(custom_header)
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
            header_data = self.get_custom_header_metadata()
            data = self.get_form_data(tk.request)
            header_data.get('links', []).append(
                Link(
                    title=data.get('new_title'),
                    url=data.get('new_url'),
                    position=len(header_data.get('links', [])),
                ))
            error = self.save_header_metadata(header_data)
            header_data['errors'] = error
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
            header_data = self.get_custom_header_metadata()
            data = self.get_form_data(tk.request)
            item = [link for link in header_data['links'] if link.title == data['to_remove']]
            try:
                header_data['links'].remove(item[0])
                error = self.save_header_metadata(header_data)
                header_data['errors'] = error
            except IndexError:
                header_data['errors'] = "Impossible to remove link."
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

        custom_header = {}
        self.save_header_metadata(custom_header)
        default_header = {
            'layout_type': 'default'
        }
        self.save_default_header_metadata(default_header)

        return tk.redirect_to(custom_header_route)

    def save_header_metadata(self, custom_header):
        try:
            self.store_data(CONFIG_SECTION, custom_header)
        except tk.ValidationError as ex:
            return ex.error_summary

    def get_custom_header_metadata(self):
        data = self.get_data(CONFIG_SECTION)
        default_data = self.get_default_custom_header_metadata()
        if not data.get('links'):
            for h in default_data.get('links', []):
                data.get('links', []).append(h)
        return data

    def save_default_header_metadata(self, custom_header):
        self.store_data(DEFAULT_CONFIG_SECTION, custom_header)

    def get_default_custom_header_metadata(self):
        return self.get_data(DEFAULT_CONFIG_SECTION)

    def store_data(self, config_key, data):
        data_dict = data.copy()
        links = []
        for item in data.get('links', []):
            links.append(item.to_dict())
        data_dict['links'] = links
        BaseCompatibilityController.store_data(config_key, data_dict)

    def get_data(self, config_key):
        data_dict = BaseCompatibilityController.get_data(config_key)
        links = []
        for item in data_dict.get('links', []):
            if isinstance(item, dict):
                item = Link(**item)
            links.append(item)
        if links:
            data_dict['links'] = links
        return data_dict
