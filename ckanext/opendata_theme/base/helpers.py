import ast
import logging

from ckan.plugins import toolkit
from ckan.plugins.toolkit import config
from packaging.version import Version

from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.opendata_theme.opengov_custom_homepage.constants import CUSTOM_NAMING


logger = logging.getLogger(__name__)


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
    showcases = []
    try:
        showcases = toolkit.get_action('ckanext_showcase_list')({}, {})
    except Exception:
        logger.debug("[opendata_theme] Error getting showcase list")
        return []
    return showcases[:num]


def groups(num=12):
    """Return a list of groups"""
    groups = []
    try:
        groups = toolkit.get_action('group_list')({}, {'all_fields': True, 'sort': 'packages'})
    except Exception:
        logger.debug("[opendata_theme] Error getting group list")
        return []
    return groups[:num]


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


def package_tracking_summary(package):
    """Return the tracking summary of a dataset"""
    tracking_summary = {}
    try:
        result = toolkit.get_action('package_show')({}, {'id': package.get('name'), 'include_tracking': True})
        if result.get('tracking_summary'):
            tracking_summary = result.get('tracking_summary')
    except Exception:
        logger.debug("[opendata_theme] Error getting dataset tracking_summary")
        return {}
    return tracking_summary


def get_group_alias():
    return str(config.get('ckan.group_alias', 'Group'))


def get_organization_alias():
    return str(config.get('ckan.organization_alias', 'Organization'))


def get_custom_name(key, default_name):
    custom_naming = toolkit.get_action('config_option_show')({'ignore_auth': True}, {"key": CUSTOM_NAMING})
    if not custom_naming:
        return default_name
    custom_naming = ast.literal_eval(custom_naming)
    name = custom_naming.get(key)
    if not name:
        return default_name
    elif not name.get('value'):
        return default_name
    else:
        return name.get('value')


def get_data(key):
    return BaseCompatibilityController.get_data(key)


def version_builder(text_version):
    return Version(text_version)


def showcase_story(story=True, num=12):
    """Return list of Showcase whose tag is story"""

    existent_showcases = showcases()
    sorted_tags = {}
    std_story_showcase = []
    for showcase in existent_showcases:
        for tag in showcase['tags']:
            if tag['name'].lower() == "story":
                std_story_showcase.append(showcase)
                continue

            story_tag = re.findall("story[ -+]?[0-9]+$", tag['name'])

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
