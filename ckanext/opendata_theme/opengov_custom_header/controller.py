# encoding: utf-8
import ast

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
from webhelpers.html import literal

from ckanext.opendata_theme.opengov_custom_header.constants import CONFIG_SECTION, CONTROLLER, DEFAULT_CONFIG_SECTION


class Header(object):
    def __init__(self, title, link, position, html=''):
        self.title = title.lower()
        self.link = link
        self.position = position
        self._html = None
        self.html = html

    def __repr__(self):
        return '{}:{}'.format(self.position, self.title)

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'position': self.position,
            'html': str(self.html)
        }

    @property
    def html(self):
        if not self._html:
            self._html = literal('<li><a href="{}">{title}</a></li>'.format(
                self.link, title=self.title))
        return literal(self._html)

    @html.setter
    def html(self, value):
        self._html = str(value)


class CustomHeaderController(admin.AdminController):
    def remove_link(self):
        if request.method == 'POST':
            header_data = self.get_custom_header_metadata()
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))
            item = [link for link in header_data['links'] if link.title == data['to_remove']]
            header_data['links'].remove(item[0])
            self.save_header_metadata(header_data)
            self.redirect_to_custom_header_page(header_data)

    def add_link(self):
        if request.method == 'POST':
            header_data = self.get_custom_header_metadata()
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))
            header_data['links'].append(
                Header(
                    title=data.get('new_title'),
                    link=data.get('new_link'),
                    position=len(header_data['links'])+1,
                ))
            self.save_header_metadata(header_data)
            self.redirect_to_custom_header_page(header_data)

    def custom_header(self):
        custom_header = self.get_custom_header_metadata()
        if request.method == 'POST':
            data = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))
            custom_header = {'links': []}
            data_len = len(data.get('link', []))
            if data_len > 1:
                for index in range(data_len):
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
            self.save_header_metadata(custom_header)
        return render('admin/custom_header.html',
                      extra_vars=custom_header)

    def redirect_to_custom_header_page(self, vars):
        redirect_to(
            controller=CONTROLLER,
            action='custom_header',
            extra_vars=vars
        )

    def reset_custom_header(self):
        custom_header = {}
        self.save_default_header_metadata(custom_header)
        self.save_header_metadata(custom_header)
        # for setting default headers from page to db
        render('admin/custom_header.html',
               extra_vars=custom_header)
        self.redirect_to_custom_header_page(custom_header)

    @staticmethod
    def save_header_metadata(custom_header):
        CustomHeaderController.store_data(CONFIG_SECTION, custom_header)

    @staticmethod
    def get_custom_header_metadata():
        data = CustomHeaderController.get_data(CONFIG_SECTION)
        default_data = CustomHeaderController.get_default_custom_header_metadata()
        if not data.get('links'):
            for h in default_data.get('links', []):
                data['links'].append(h)
        return data

    @staticmethod
    def save_default_header_metadata(custom_header):
        CustomHeaderController.store_data(DEFAULT_CONFIG_SECTION, custom_header)

    @staticmethod
    def get_default_custom_header_metadata():
        return CustomHeaderController.get_data(DEFAULT_CONFIG_SECTION)

    @staticmethod
    def store_data(config_key, data):
        data_dict = data.copy()
        links = []
        for item in data.get('links', []):
            links.append(item.to_dict())
        data_dict['links'] = links
        get_action('config_option_update')({}, {config_key: data_dict})

    @staticmethod
    def get_data(config_key):
        data = get_action('config_option_show')({}, {"key": config_key})
        if not data:
            return {}
        try:
            data_dict = ast.literal_eval(data)
        except ValueError:
            data_dict = data
        links = []
        for item in data_dict.get('links', []):
            links.append(Header(**item))
        data_dict['links'] = links
        return data_dict
