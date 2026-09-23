from flask import Blueprint, make_response
import ckanext.opendata_theme.opengov_custom_theme.utils as utils
from ckanext.opendata_theme.opengov_custom_theme.controller import ResourceTypeController

datastore_dictionary = Blueprint(u'datastore_dictionary', __name__)


def dictionary_download(resource_id):
    response = make_response()
    response.headers[u'content-type'] = u'application/octet-stream'
    return utils.dictionary_download(resource_id, response)


datastore_dictionary.add_url_rule(u'/datastore/dictionary_download/<resource_id>', view_func=dictionary_download)


resource_types = Blueprint(u'resource_types', __name__, url_prefix=u'/ckan-admin')

resource_types.add_url_rule(
    u'/resource_types', methods=[u'GET', u'POST'],
    view_func=ResourceTypeController().manage_resource_types
)
resource_types.add_url_rule(
    u'/reset_resource_types', methods=[u'GET', u'POST'],
    view_func=ResourceTypeController().reset_resource_types
)


def get_blueprints():
    return [datastore_dictionary, resource_types]
