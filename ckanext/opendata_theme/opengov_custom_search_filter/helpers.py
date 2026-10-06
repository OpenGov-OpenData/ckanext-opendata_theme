import ast
import json
import re

from six import string_types

import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import config, g

from ckanext.opendata_theme.opengov_custom_search_filter.constants import (
    RESOURCE_TYPE_CATEGORIES_KEY,
    RESOURCE_TYPE_FILTER_ENABLED_KEY,
    DEFAULT_RESOURCE_TYPE_CATEGORIES,
)

_RESOURCE_TYPE_KEY_RE = re.compile(r'^[a-z0-9_-]+$')
_MAX_FORMATS_PER_CATEGORY = 200
_RESOURCE_TYPE_CONFIG_CACHE_ATTR = '_opendata_theme_resource_type_config'


def resource_type_categories_validator(value):
    if isinstance(value, string_types):
        value = value.strip()
        if not value:
            raise toolkit.Invalid(
                'Resource Type Categories must not be empty (use "Reset to Default" to restore the defaults)'
            )
        try:
            value = json.loads(value)
        except ValueError:
            raise toolkit.Invalid('Resource Type Categories must be valid JSON')
    if not isinstance(value, dict):
        raise toolkit.Invalid('Resource Type Categories must be a JSON object')
    for key, item in value.items():
        if not isinstance(key, string_types) or not _RESOURCE_TYPE_KEY_RE.match(key):
            raise toolkit.Invalid(
                'Category key "{}" must contain only lowercase letters, numbers, '
                'hyphens, and underscores (it is used in the URL as ?ext_res_type={})'.format(key, key)
            )
        if not isinstance(item, dict):
            raise toolkit.Invalid('Category "{}" must be a JSON object'.format(key))
        label = item.get('label')
        if not isinstance(label, string_types) or not label.strip():
            raise toolkit.Invalid('Category "{}" must include a non-empty "label"'.format(key))
        if 'enabled' in item and not isinstance(item['enabled'], bool):
            raise toolkit.Invalid('Category "{}" "enabled" must be true or false'.format(key))
        formats = item.get('formats')
        if not isinstance(formats, list) or not formats:
            raise toolkit.Invalid('Category "{}" must include a non-empty "formats" list'.format(key))
        if len(formats) > _MAX_FORMATS_PER_CATEGORY:
            raise toolkit.Invalid(
                'Category "{}" has {} formats, which exceeds the limit of {}'.format(
                    key, len(formats), _MAX_FORMATS_PER_CATEGORY
                )
            )
        if not all(isinstance(f, string_types) and f.strip() for f in formats):
            raise toolkit.Invalid('Category "{}" "formats" must be a list of non-empty strings'.format(key))
    return value


def get_resource_type_config():
    try:
        cached = getattr(g, _RESOURCE_TYPE_CONFIG_CACHE_ATTR, None)
    except Exception:
        cached = None
    if cached is not None:
        return cached

    raw = toolkit.get_action('config_option_show')({'ignore_auth': True}, {'key': RESOURCE_TYPE_CATEGORIES_KEY})
    if raw is None:
        data = DEFAULT_RESOURCE_TYPE_CATEGORIES
    else:
        try:
            data = ast.literal_eval(raw) if isinstance(raw, string_types) else raw
        except (ValueError, SyntaxError):
            data = DEFAULT_RESOURCE_TYPE_CATEGORIES
        if not isinstance(data, dict):
            data = DEFAULT_RESOURCE_TYPE_CATEGORIES

    try:
        setattr(g, _RESOURCE_TYPE_CONFIG_CACHE_ATTR, data)
    except Exception:
        pass
    return data


def get_resource_type_formats():
    return {k: v.get('formats', []) for k, v in get_resource_type_config().items() if v.get('enabled', False)}


def get_resource_type_categories():
    enabled = toolkit.asbool(config.get(RESOURCE_TYPE_FILTER_ENABLED_KEY) or False)
    if not enabled:
        return []
    return [
        {'name': k, 'label': v.get('label', k)}
        for k, v in get_resource_type_config().items()
        if v.get('enabled', False)
    ]


def get_active_res_type():
    try:
        return toolkit.request.params.get('ext_res_type', '')
    except Exception:
        return ''


def escape_solr_value(value):
    return value.replace('\\', '\\\\').replace('"', '\\"')
