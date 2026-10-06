import json

import pytest

import ckan.tests.helpers as ckan_helpers

from ckanext.opendata_theme.opengov_custom_search_filter.constants import (
    DEFAULT_RESOURCE_TYPE_CATEGORIES,
    RESOURCE_TYPE_FILTER_ENABLED_KEY,
)
from ckanext.opendata_theme.tests.helpers import do_get, do_post, get_env

ADMIN_URL = '/ckan-admin/resource_types'
RESET_URL = '/ckan-admin/reset_resource_types'
CATEGORIES = {
    'audio': {'label': 'Audio Files', 'enabled': True, 'formats': ['MP3', 'WAV']},
    'tabular': {'label': 'Tabular Data', 'enabled': True, 'formats': ['CSV']},
}


def _text(response):
    return response.get_data(as_text=True) if hasattr(response, 'get_data') else str(response)


def _save(app, categories=None, enabled=True, raw=None):
    data = {'save': '', 'categories_json': raw if raw is not None else json.dumps(categories)}
    if enabled:
        data['enabled'] = 'true'
    return do_post(app, ADMIN_URL, data, is_sysadmin=True)


pytestmark = [
    pytest.mark.usefixtures('with_plugins', 'clean_db', 'with_request_context'),
    pytest.mark.ckan_config('ckan.plugins', 'opengov_custom_theme opengov_custom_search_filter'),
]


def test_page_requires_sysadmin(app):
    assert '403' in _text(do_get(app, ADMIN_URL, is_sysadmin=False))


def test_page_shows_defaults(app):
    response = _text(do_get(app, ADMIN_URL, is_sysadmin=True))
    assert 'Manage Resource Type Filter' in response
    assert 'Tabular Data' in response


def test_save_shows_success_and_enables_filter(app):
    response = _text(_save(app, CATEGORIES))
    assert 'Resource Type Filter settings updated.' in response
    assert ckan_helpers.call_action('config_option_show', key=RESOURCE_TYPE_FILTER_ENABLED_KEY) == 'true'


def test_site_still_works_after_saving_regression(app):
    # Saving once corrupted the enabled flag to the string "None", which then
    # raised ValueError on every search page and on this admin page.
    _save(app, CATEGORIES)
    assert 'Audio Files' in _text(do_get(app, ADMIN_URL, is_sysadmin=True))
    assert 'Audio Files' in _text(app.get('/dataset/', extra_environ=get_env(True)))


def test_unchecking_enabled_hides_filter(app):
    _save(app, CATEGORIES, enabled=False)
    assert ckan_helpers.call_action('config_option_show', key=RESOURCE_TYPE_FILTER_ENABLED_KEY) == 'false'
    assert 'Audio Files' not in _text(app.get('/dataset/', extra_environ=get_env(True)))


@pytest.mark.parametrize('raw', ['', '   ', 'not json', '[]', '{"Bad Key": {"label": "X", "formats": ["A"]}}'])
def test_invalid_input_is_rejected(app, raw):
    response = _text(_save(app, raw=raw))
    assert 'Resource Type Filter settings updated.' not in response
    assert 'error' in response.lower()


def test_new_category_filters_search_results(app):
    _save(app, CATEGORIES)
    response = app.get('/dataset/?ext_res_type=audio', extra_environ=get_env(True))
    assert response.status_code == 200


def test_reset_requires_post(app):
    app.get(RESET_URL, extra_environ=get_env(True), status=405)


def test_reset_restores_defaults(app):
    _save(app, CATEGORIES)
    do_post(app, RESET_URL, {}, is_sysadmin=True)
    response = _text(do_get(app, ADMIN_URL, is_sysadmin=True))
    assert 'Audio Files' not in response
    for category in DEFAULT_RESOURCE_TYPE_CATEGORIES.values():
        assert category['label'] in response
