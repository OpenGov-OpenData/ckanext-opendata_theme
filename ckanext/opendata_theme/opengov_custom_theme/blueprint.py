from flask import Blueprint, make_response
import ckanext.opendata_theme.opengov_custom_theme.utils as utils

datastore_dictionary = Blueprint(u'datastore_dictionary', __name__)


def dictionary_download(resource_id):
    response = make_response()
    response.headers[u'content-type'] = u'application/octet-stream'
    return utils.dictionary_download(resource_id, response)


datastore_dictionary.add_url_rule(u'/datastore/dictionary_download/<resource_id>', view_func=dictionary_download)


def get_blueprints():
    return [datastore_dictionary]
