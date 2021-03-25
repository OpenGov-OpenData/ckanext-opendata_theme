# encoding: utf-8
import six
from ckan.logic import ValidationError
from ckan.plugins.toolkit import (
    render,
    request
)
try:
    from webhelpers.html import literal
except ModuleNotFoundError:
    from ckan.lib.helpers import literal

from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, DEFAULT_CONFIG_SECTION
from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController


class Header(object):
    def __init__(self, title, link, position, active=False):
        self.title = six.text_type(title).lower()
        self.link = six.text_type(link)
        self.position = position
        self._html = None
        self.active = active

    def __repr__(self):
        return '{}:{}'.format(self.position, self.title)

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'position': self.position,
            'active': self.active,
        }

    @property
    def html(self):
        if not self._html:
            self._html = literal('<li><a href="{}">{title}</a></li>'.format(
                self.link, title=self.title))
        return literal(self._html)


class CustomHeaderController(BaseCompatibilityController):
    redirect_to_action_kwargs = dict(endpoint='custom-header.custom_header')

    def remove_link(self):
        if request.method == 'POST':
            header_data = self.get_custom_header_metadata()
            data = self.get_form_data(request)
            item = [link for link in header_data['links'] if link.title == data['to_remove']]
            try:
                header_data['links'].remove(item[0])
                error = self.save_header_metadata(header_data)
                header_data['errors'] = error
            except IndexError:
                header_data['errors'] = "Impossible to remove link."
            return self.redirect_to(header_data)

    def add_link(self):
        if request.method == 'POST':
            header_data = self.get_custom_header_metadata()
            data = self.get_form_data(request)
            header_data.get('links', []).append(
                Header(
                    title=data.get('new_title'),
                    link=data.get('new_link'),
                    position=len(header_data.get('links', [])),
                ))
            error = self.save_header_metadata(header_data)
            header_data['errors'] = error
            return render('admin/custom_header.html',
                          extra_vars=header_data)

    def custom_header(self):
        custom_header = self.get_custom_header_metadata()
        if not custom_header:
            # this block is required for base initialization
            # it happens only once when default custom header metadata is not set
            # because it is set in build_pages_nav_main helper function which is called
            # during the page rendering.
            # reset_custom_header is able to render the page in the background for setting default metadata.
            self.reset_custom_header()
        if request.method == 'POST':
            data = self.get_form_data(request)
            custom_header = {
                'links': [],
                'layout_type': data.get('layout_type', 'default')
            }
            if isinstance(data.get('link'), list):
                for index in range(len(data.get('link'))):
                    custom_header['links'].append(Header(
                        title=data['title'][index],
                        link=data['link'][index],
                        position=data['position'][index],
                    ))
            else:
                custom_header['links'].append(Header(
                    title=data['title'],
                    link=data['link'],
                    position=data['position'],
                ))
            error = self.save_header_metadata(custom_header)
            custom_header['errors'] = error

        return render('admin/custom_header.html',
                      extra_vars=custom_header)

    def reset_custom_header(self):
        custom_header = {}
        self.save_header_metadata(custom_header)
        return self.redirect_to(custom_header)

    def save_header_metadata(self, custom_header):
        try:
            self.store_data(CONFIG_SECTION, custom_header)
        except ValidationError as ex:
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
            links.append(Header(**item))
        if links:
            data_dict['links'] = links
        return data_dict
