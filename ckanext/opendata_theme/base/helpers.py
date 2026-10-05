import ast
import bleach
import json
import logging
import re
import string

import ckan.model as model

from six import string_types

from ckan.plugins import toolkit
from ckan.plugins.toolkit import config, c, g
from packaging.version import Version

from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.opendata_theme.opengov_custom_homepage.constants import CUSTOM_NAMING

if toolkit.check_ckan_version(min_version='2.9.0'):
    from ckan.lib.helpers import literal
else:
    from webhelpers.html import literal


logger = logging.getLogger(__name__)


def abbreviate_name(name):
    """Returns an abbreviation of a name"""
    name_snippets = name.split()
    result = ''
    for s in name_snippets:
        result += s[0].upper()
    return result


def dataset_count():
    """Return a count of all datasets"""
    count = 0
    try:
        result = toolkit.get_action('package_search')({}, {'rows': 1})
        if result.get('count'):
            count = result.get('count')
    except Exception:
        logger.debug("[opendata_theme] Error getting dataset count")
        return 0
    return count


def showcases(num=24):
    """Return a list of showcases"""
    sorted_showcases = []
    try:
        showcases = toolkit.get_action('ckanext_showcase_list')({}, {})
        sorted_showcases = sorted(showcases, key=lambda k: k.get('metadata_modified'), reverse=True)
    except Exception:
        logger.debug("[opendata_theme] Error getting showcase list")
        return []
    return sorted_showcases[:num]


def groups(num=12):
    """Return a list of groups"""
    sorted_groups = []
    try:
        groups = toolkit.get_action('group_list')({}, {'all_fields': True})
        sorted_groups = sorted(groups, key=lambda k: (-int(k.get('package_count')), k.get('title')))
    except Exception:
        logger.debug("[opendata_theme] Error getting group list")
        return []
    return sorted_groups[:num]


def popular_datasets(num=5):
    """Return a list of popular datasets."""
    datasets = []
    try:
        search = toolkit.get_action('package_search')({}, {'rows': num, 'sort': 'views_recent desc'})
        if search.get('results'):
            datasets = search.get('results')
    except Exception:
        logger.debug("[opendata_theme] Error getting popular datasets")
        return []
    return datasets[:num]


def recent_datasets(num=5):
    """Return a list of recently updated/created datasets."""
    sorted_datasets = []
    try:
        datasets = toolkit.get_action('current_package_list_with_resources')({}, {'limit': num})
        if datasets:
            sorted_datasets = sorted(datasets, key=lambda k: k['metadata_modified'], reverse=True)
    except Exception:
        logger.debug("[opendata_theme] Error getting recently updated/created datasets")
        return []
    return sorted_datasets[:num]


def new_datasets(num=3):
    """Return a list of the newly created datasets."""
    datasets = []
    try:
        search = toolkit.get_action('package_search')({}, {'rows': num, 'sort': 'metadata_created desc'})
        if search.get('results'):
            datasets = search.get('results')
    except Exception:
        logger.debug("[opendata_theme] Error getting newly created datasets")
        return []
    return datasets[:num]


def get_user_uuid():
    """Return the user platform_uuid for a given email, if there is a token for that email"""
    try:
        user = c.userobj or g.userobj
        if user:
            try:
                from ckanext.opengov.auth.db import UserToken
                user_token = model.Session.query(UserToken).filter_by(user_name=user.email).first()
                if user_token:
                    return user_token.platform_uuid
            except Exception as e:
                logger.debug("[opendata_theme] Error querying user token in get_user_uuid: {}".format(e))
            return user.id
        return None
    except Exception as e:
        logger.debug("[opendata_theme] Error in get_user_uuid: {}".format(e))
        return None


def package_tracking_summary(package):
    """Return the tracking summary of a dataset"""
    tracking_summary = {}
    try:
        result = toolkit.get_action('package_show')({}, {'id': package.get('name'), 'include_tracking': True})
        if result.get('tracking_summary'):
            tracking_summary = result.get('tracking_summary')
    except Exception:
        logger.debug("[opendata_theme] Error getting dataset tracking_summary")
        return {
            'total': 0,
            'recent': 0
        }
    return tracking_summary


def is_data_dict_active(ddict):
    """"Returns True if data dictionary is populated"""
    for col in ddict:
        info = col.get('info', {})
        if info.get('label') or info.get('notes'):
            return True
    return False


def get_segment_writekey():
    return str(config.get('ckan.segment_writekey', ''))


def get_entity_id():
    return str(config.get('ckanext.opengov.datastore.entity_id', 'controlpanel'))


def get_group_alias():
    return str(config.get('ckan.group_alias', 'Group'))


def get_organization_alias():
    return str(config.get('ckan.organization_alias', 'Organization'))


def _get_custom_value(key, default_value=''):
    """Internal helper to retrieve custom values from CUSTOM_NAMING config."""
    custom_naming = toolkit.get_action('config_option_show')({'ignore_auth': True}, {"key": CUSTOM_NAMING})
    if not custom_naming:
        return default_value
    custom_naming = ast.literal_eval(custom_naming)
    item = custom_naming.get(key)
    if not item:
        return default_value
    else:
        return toolkit.h.markdown_extract(item.get('value', default_value))


def get_custom_name(key, default_name):
    return _get_custom_value(key, default_name)


def get_custom_explanation(key, default_explanation=''):
    return _get_custom_value(key, default_explanation)


def get_data(key):
    return BaseCompatibilityController.get_data(key)


def version_builder(text_version):
    return Version(text_version)


def get_story_banner():
    """Return a showcase with a specific story tag"""
    existent_showcases = showcases()
    for showcase in existent_showcases:
        for tag in showcase['tags']:
            if tag['name'].lower() in ['story banner', 'story-banner', 'story+banner']:
                return showcase


def showcase_story(story=True, num=12):
    """Return list of Showcase whose tag is story"""

    existent_showcases = showcases()
    sorted_tags = {}
    std_story_showcase = []
    for showcase in existent_showcases:
        for tag in showcase['tags']:
            if tag['name'].lower() == 'story':
                std_story_showcase.append(showcase)
                continue

            story_tag = re.findall("story[ +-]?[0-9]+$", tag['name'])

            if len(story_tag) > 0:
                key = re.findall(r'\d+', story_tag[0])
                if int(key[0]) in sorted_tags:
                    temp = sorted_tags[int(key[0])]
                    temp.append(showcase)
                    sorted_tags[int(key[0])] = temp
                else:
                    temp = []
                    temp.append(showcase)
                    sorted_tags[int(key[0])] = temp

    dict_keys_sorted = sorted(list(sorted_tags))

    sorted_showcases = []
    for key in dict_keys_sorted:
        showcases_tags_num = sorted_tags.get(key)
        for showcase in showcases_tags_num:
            sorted_showcases.append(showcase)
    for showcase in std_story_showcase:
        if showcase not in sorted_showcases:
            sorted_showcases.append(showcase)

    if story is False:
        default_showcases = []
        for showcase in existent_showcases:
            if showcase not in sorted_showcases:
                default_showcases.append(showcase)
        return default_showcases
    else:
        return sorted_showcases


def get_value_from_extras(extras, key):
    value = ''
    for item in extras:
        if item.get('key') == key:
            value = item.get('value')
    return value


def custom_page_exists(page_id):
    try:
        if not page_id:
            return False
        search_doc = toolkit.get_action('ckanext_pages_show')({}, {'page': page_id})
        if search_doc.get('content') and not search_doc.get('private'):
            return True
    except Exception:
        logger.debug("[opendata_theme] Error in retrieving page")
    return False


def check_characters(value):
    if value in ['', None]:
        return False
    if value and set(value) <= set(string.printable):
        return False
    return True


def sanityze_all_html(text):
    cleaned_text = bleach.clean(text, tags=[], attributes={})
    return cleaned_text


def value_should_be_not_empty(field_name='text'):
    def decorator(func):
        def _wrap(value):
            if not value:
                raise toolkit.Invalid('Missing {}'.format(field_name))
            return func(value)
        return _wrap
    return decorator


def value_should_be_shorter_than_length(field_name='Field', length=30):
    def decorator(func):
        def _wrap(value):
            if len(value) > length:
                raise toolkit.Invalid(
                    '{} is too long. Maximum {} characters allowed for {}'.format(field_name, length, value)
                )
            return func(value)
        return _wrap
    return decorator


RESOURCE_TYPE_CATEGORIES_KEY = 'ckanext.opendata_theme.resource_type_categories'
RESOURCE_TYPE_FILTER_ENABLED_KEY = 'ckanext.opendata_theme.resource_type_filter_enabled'

DEFAULT_RESOURCE_TYPE_CATEGORIES = {
    'tabular': {
        'label': 'Tabular Data',
        'enabled': True,
        'formats': ['CSV', 'XLS', 'XLSX', 'ODS', 'TSV', 'XLSM', 'csv', 'xls', 'xlsx', 'ods', 'tsv', 'xlsm'],
    },
    'documents': {
        'label': 'Documents',
        'enabled': True,
        'formats': ['PDF', 'DOC', 'DOCX', 'RTF', 'ODT', 'TXT', 'pdf', 'doc', 'docx', 'rtf', 'odt', 'txt'],
    },
    'images': {
        'label': 'Images',
        'enabled': False,
        'formats': [
            'PNG', 'JPG', 'JPEG', 'GIF', 'TIFF', 'SVG', 'BMP', 'WEBP', 'GeoTIFF',
            'png', 'jpg', 'jpeg', 'gif', 'tiff', 'svg', 'bmp', 'webp',
        ],
    },
    'maps': {
        'label': 'Maps',
        'enabled': True,
        'formats': [
            'GeoJSON', 'KML', 'KMZ', 'SHP', 'GML', 'WFS', 'WMS',
            'geojson', 'kml', 'kmz', 'shp', 'gml', 'wfs', 'wms',
            'Shapefile', 'shapefile', 'ESRI REST', 'esri rest',
        ],
    },
}


_RESOURCE_TYPE_KEY_RE = re.compile(r'^[a-z0-9_-]+$')
_MAX_FORMATS_PER_CATEGORY = 200


def resource_type_categories_validator(value):
    if isinstance(value, string_types):
        value = value.strip()
        if not value:
            return {}
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


_RESOURCE_TYPE_CONFIG_CACHE_ATTR = '_opendata_theme_resource_type_config'


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


def escape_solr_value(value):
    return value.replace('\\', '\\\\').replace('"', '\\"')


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


def get_default_extent():
    """
    Return default extent to use with spatial widget
    If none is configured a bounding box of the continental US is returned
    """
    return config.get(
        'ckanext.spatial.default_extent',
        '{ "type": "Polygon", \
           "coordinates": [[[-124.7844079,24.7433195], \
            [-66.9513812,24.7433195],[-66.9513812,49.3457868], \
            [-124.7844079,49.3457868],[-124.7844079,24.7433195]]] }'
    )


def get_footer_script_snippet():
    pattern = r'<script\b[^>]*>(.*?)<\/script>'
    script_snippet = toolkit.config.get('ckanext.opendata_theme.script_snippet', '')
    if not script_snippet:
        return False
    match = re.match(pattern, script_snippet, re.IGNORECASE)
    if not bool(match):
        return False
    return literal(script_snippet)
