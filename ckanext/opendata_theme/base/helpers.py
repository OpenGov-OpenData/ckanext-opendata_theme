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
