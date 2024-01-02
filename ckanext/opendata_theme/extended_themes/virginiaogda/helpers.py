# encoding: utf-8
import logging

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins.toolkit as tk

from ckan.model.package import Package
from ckan.model.package_extra import PackageExtra

log = logging.getLogger(__name__)


def get_featured_datasets():
    """
    Returns a list of featured datasets
    """
    featured_datasets = []
    try:
        featured_datasets = model.Session.query(Package)\
            .join(PackageExtra)\
            .filter(PackageExtra.key == 'featured_dataset')\
            .filter(PackageExtra.value == 'yes')\
            .filter(Package.state == 'active')\
            .filter(Package.private.is_(False))\
            .order_by(PackageExtra.value) \
            .all()
    except Exception as e:
        logging.error('Error getting featured datasets: %s', e)
    featured_datasets_dict_list = h.convert_to_dict('package',
                                                    featured_datasets)
    return featured_datasets_dict_list


def get_all_resource_count():
    """
    Returns a sum of all resources
    """
    q = model.Session.query(model.Resource)\
        .filter(model.Resource.state == 'active')
    data = {'total_resources': q.count()}
    return data


def get_resource_info(resource_id):
    """
    Returns a dictionary of resource information
    """
    res_info = {}
    try:
        datastore_info = tk.get_action('datastore_info')({}, {'id': resource_id})
        res_info['columns'] = len(datastore_info.get('schema').keys())
        res_info['rows'] = datastore_info.get('meta').get('count')
    except (tk.ObjectNotFound, tk.NotAuthorized):
        log.debug("[opendata_theme] Datastore info not found")
    return res_info
