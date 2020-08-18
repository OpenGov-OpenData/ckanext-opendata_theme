import ast

from ckan.plugins import toolkit


def dataset_count():
    """Return a count of all datasets"""
    count = 0
    result = toolkit.get_action('package_search')({}, {'rows': 1})
    if result.get('count'):
        count = result.get('count')
    return count


def showcases(num=24):
    """Return a list of showcases"""
    sorted_showcases = []
    showcases = toolkit.get_action('ckanext_showcase_list')({}, {})
    sorted_showcases = sorted(showcases, key=lambda k: k.get('position'))
    return sorted_showcases[:num]


def groups(num=12):
    """Return a list of groups"""
    groups = toolkit.get_action('group_list')({}, {'all_fields': True, 'sort': 'packages'})
    return groups[:num]


def recent_datasets(num=5):
    """Return a list of recent datasets."""
    sorted_datasets = []
    datasets = toolkit.get_action('current_package_list_with_resources')({}, {'limit': num})
    if datasets:
        sorted_datasets = sorted(datasets, key=lambda k: k['metadata_modified'], reverse=True)
    return sorted_datasets[:num]


def new_datasets(num=3):
    """Return a list of the newest datasets."""
    datasets = []
    search = toolkit.get_action('package_search')({}, {'rows': num, 'sort': 'metadata_created desc'})
    if search.get('results'):
        datasets = search.get('results')
    return datasets[:num]


def popular_datasets(num=5):
    """Return a list of popular datasets."""
    datasets = []
    search = toolkit.get_action('package_search')({}, {'rows': num, 'sort': 'views_recent desc'})
    if search.get('results'):
        datasets = search.get('results')
    return datasets[:num]


def get_package_metadata(package):
    """Return the metadata of a dataset"""
    result = {}
    try:
        result = toolkit.get_action('package_show')(None, {'id': package.get('name'), 'include_tracking': True})
    except:
        print "[og_theme] Error in retrieving dataset metadata for " + str(package)
    return result


def get_custom_name(key, default_name):
    custom_naming = toolkit.get_action('config_option_show')({}, {"key": "ckanext.opendata_theme.custom_naming"})
    if not custom_naming:
        return default_name
    custom_naming = ast.literal_eval(custom_naming)
    name = custom_naming.get(key)
    if not name:
        return default_name
    elif not name['value']:
        return default_name
    else:
        return name['value']
