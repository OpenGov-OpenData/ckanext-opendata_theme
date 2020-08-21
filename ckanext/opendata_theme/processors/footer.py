import ast
import uuid
from collections import defaultdict

import validators
from ckan.plugins.toolkit import (
    get_action
)

from ckanext.opendata_theme.constants import DEFAULT_FOOTER_LINKS, EMPTY_LINK


class Link:

    def __init__(self, url, text, img_src=None):
        # Add errors block on template
        if not validators.url(url):
            raise ValueError("Url format is not valid")
        if not text:
            raise ValueError("Text of link should not be empty")
        self.url = url
        self.text = text
        self.img_src = img_src if img_src else ""

    def asdict(self):
        return {
            "text": self.text,
            "value": self.url,
            "img": self.img_src
        }


class CustomFooterProcessor:

    def get_all_links_from_defaults(self):
        # No idea why list is not saved for ckan.
        # So I saved them in dict to make it working at least
        result = defaultdict(list)
        for column, links in DEFAULT_FOOTER_LINKS.items():
            for link in links:
                result[str(uuid.uuid4())] = link
        return result

    def get_links_for_columns(self):
        columns_with_links = get_action('config_option_show')(
            {}, {"key": "ckanext.opendata_theme.footer_columns_links"}
        )
        if not columns_with_links:
            get_action('config_option_update')(
                {},
                {"ckanext.opendata_theme.footer_columns_links": DEFAULT_FOOTER_LINKS}
            )
            return DEFAULT_FOOTER_LINKS['1'], DEFAULT_FOOTER_LINKS['2'], DEFAULT_FOOTER_LINKS['3']
        if isinstance(columns_with_links, basestring):
            columns_with_links = ast.literal_eval(columns_with_links)
        return columns_with_links['1'], columns_with_links['2'], columns_with_links['3']

    def reset_columns_links(self):
        get_action('config_option_update')(
            {},
            {"ckanext.opendata_theme.footer_columns_links": DEFAULT_FOOTER_LINKS}
        )

    def add_new_link(self, data):
        if not data['new-link-url'] or not data['new-link-text']:
            # Add Skip for empty
            return
        try:
            new_link = Link(
                url=data['new-link-url'],
                text=data['new-link-text'])
        except ValueError as e:
            raise e
        else:
            all_links = get_action('config_option_show')(
                {}, {"key": "ckanext.opendata_theme.all_footer_links"}
            )
            all_links = ast.literal_eval(all_links)
            all_links[str(uuid.uuid4())] = new_link.asdict()
            get_action('config_option_update')(
                {},
                {"ckanext.opendata_theme.all_footer_links": all_links}
            )

    def find_link_by_value(self, all_links, value):
        for _, link in all_links.items():
            if link['value'] == value:
                return link

    def update_column_with_new_link(self, all_columns, new_link_data, form_link_id):
        for link in all_columns:
            if link['id'] == form_link_id:
                link['text'] = new_link_data['text']
                link['value'] = new_link_data['value']
                # link['img'] = new_link_data['text']
                # Todo add img to this stuff
                return

    def update_columns(self, data, all_links):
        col1, col2, col3 = self.get_links_for_columns()
        all_columns = col1 + col2 + col3
        for form_link_id, new_link_value in data.items():
            if not form_link_id.startswith('custom-link-'):
                continue
            if new_link_value == "":
                link = EMPTY_LINK.copy()
            else:
                link = self.find_link_by_value(all_links, new_link_value)
            if not link:
                raise ValueError("Link value is not in proper list")
            self.update_column_with_new_link(all_columns, link, form_link_id)

        new_columns = {
                "1": all_columns[0:5],
                "2": all_columns[5:10],
                "3": all_columns[10:15]
            }
        get_action('config_option_update')(
            {},
            {"ckanext.opendata_theme.footer_columns_links": new_columns}
        )

    def parse_form_data(self, form_data, all_links):
        self.add_new_link(form_data)
        self.update_columns(form_data, all_links)
