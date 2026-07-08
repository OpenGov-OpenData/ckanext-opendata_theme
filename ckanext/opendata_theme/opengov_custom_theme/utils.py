import unicodecsv as csv
from ckanapi.datapackage import _convert_to_datapackage_resource
from ckan.plugins.toolkit import (
    ObjectNotFound,
    NotAuthorized,
    abort,
    check_ckan_version,
    get_action,
    _
)


def dictionary_filename(resource_id):
    # Reuse ckanext-downloadall's naming so the data dictionary matches its
    # saved resource files. _convert_to_datapackage_resource is a private
    # ckanapi symbol, so guard against it (or resource_show) raising and fall
    # back to the resource id.
    try:
        resource = get_action('resource_show')(None, {'id': resource_id})
        base = _convert_to_datapackage_resource(resource).get('name', resource_id)
    except Exception:
        base = resource_id
    return '{base}-data-dictionary.csv'.format(base=base)


def dictionary_download(resource_id, response):
    try:
        resource_datastore = get_action('datastore_search')(None, {
            'resource_id': resource_id,
            'limit': 0
        })
    except (ObjectNotFound, NotAuthorized):
        abort(404, _('Resource not found'))

    fields = [f for f in resource_datastore['fields'] if not f['id'].startswith('_')]
    header = ['column', 'type', 'label', 'description']

    if hasattr(response, u'headers'):
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-disposition'] = (
            'attachment; filename="{filename}"'.format(
                filename=dictionary_filename(resource_id)))

    if check_ckan_version(min_version='2.9.0'):
        wr = csv.writer(response.stream, encoding='utf-8')
    else:
        wr = csv.writer(response, encoding='utf-8')

    wr.writerow(col for col in header)
    for field in fields:
        field_info = field.get('info', {})
        row = [field['id'], field['type'], field_info.get('label', ''), field_info.get('notes', '')]
        wr.writerow(item for item in row)

    return response
