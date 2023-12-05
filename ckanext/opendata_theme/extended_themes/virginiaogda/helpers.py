# encoding: utf-8
import logging

import ckan.lib.helpers as h
import ckan.model as model
from ckan.lib.search import make_connection

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
            .filter(Package.private == False)\
            .order_by(PackageExtra.value)\
            .all()  # noqa: E712
    except Exception as e:
        logging.error('Error getting featured datasets: %s', e)
    featured_datasets_dict_list = h.convert_to_dict('package', featured_datasets)
    return featured_datasets_dict_list


def get_all_resource_count():
    """
    Returns a sum of all resources
    """
    q = model.Session.query(model.Resource).filter(model.Resource.state == 'active')
    data = {'total_resources': q.count()}
    return data


def get_contributors_count():
    solr = make_connection()

    total = 0  # total number of contributors
    results = (
        solr.search(
            '*:*',
            **{
                'fq': '+capacity:public +state:active',
                'facet': 'true',
                'facet.pivot': 'id,author',
                'facet.pivot.mincount': 1,
                'facet.limit': -1,
            }
        )
        .facets.get('facet_pivot', {})
        .get('id,author', [])
    )
    log.info('Number of packages with authors: %s', len(results))

    # turn the counts into a lookup from package_id -> number of authors. Note that the number of
    # authors only includes authors we haven't seen before to avoid counting authors of multiple
    # packages more than once
    counts = {}
    seen_authors = set()
    for hit in results:
        package_id = hit['value']
        package_authors = set(author['value'] for author in hit.get('pivot', []))
        # figure out which authors have not been counted yet
        unseen_authors = package_authors.difference(seen_authors)
        counts[package_id] = len(unseen_authors)
        seen_authors.update(unseen_authors)

    # retrieve the packages in the database ordered by creation time. We need this because we can't
    # order the solr facets by created date
    order = list(
        model.Session.query(model.Package.id, model.Package.metadata_created)
        .filter(model.Package.private == False)  # noqa: E712
        .filter(model.Package.state == model.State.ACTIVE)
        .order_by(model.Package.metadata_created)
    )
    # get toal number of contributors
    for package_id, created in order:
        total += counts.get(package_id, 0)
    log.info('Total number of contributors: %s', total)
    return total
