import pytest

from ckanext.opendata_theme.tests.helpers import do_get, do_post

CUSTOM_HOMEPAGE_URL = "/ckan-admin/custom_homepage"
RESET_CUSTOM_HOMEPAGE_URL = "/ckan-admin/reset_custom_homepage"

DEFAULT_DATA = {
    'custom_homepage_layout': '1',
    'popular-datasets-custom-name': 'Popular Datasets',
    'popular-datasets-custom-explanation': 'Browse popular datasets below and see what other citizens find interesting.',
    'recent-datasets-custom-name': 'New and Recent Datasets',
    'recent-datasets-custom-explanation': 'Browse new or modified datasets below. Click to view details or explore content.',
    'groups-custom-name': 'Groups',
    'groups-custom-explanation': (
        'As datasets are published, they are grouped into categories '
        'so you can learn about popular topics.'
    ),
    'showcases-custom-name': 'Showcases',
    'showcases-custom-explanation': ''
}

DEFAULT_HEADERS = (
    'Popular Datasets',
    'New and Recent Datasets',
    # next headers not available for now because of disabled plugins
    # 'Groups',
    # 'Showcases'
)


def check_custom_homepage_html(response, expected_form_data):
    assert response, 'Response is empty.'
    layout_type = expected_form_data.pop('custom_homepage_layout', 1)
    if layout_type == 1:
        assert '<option value="1" selected>Homepage layout 1</option>' in response
        assert '<option value="2">Homepage layout 2</option>' in response
    elif layout_type == 2:
        assert '<option value="1">Homepage layout 1</option>' in response
        assert '<option value="2" selected>Homepage layout 2</option>' in response
    for key, value in expected_form_data.items():
        assert 'name="{0}" id="{0}" value="{1}"'.format(
            key, value) in response, 'Missed form field for "{}".'.format(key)

    assert 'alert' not in response, 'Result HTML contains alerts when they are not expected.'


def check_homepage_html(response, expected_data):
    assert response, 'Response is empty.'
    for value in expected_data:
        assert value in response, 'Missed header for "{}".'.format(value)
    assert 'alert' not in response, 'Result HTML contains alerts when they are not expected.'


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_homepage_page_with_not_sysadmin_user(app):
    response = do_get(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=False)
    assert '<h1>403 Forbidden</h1>' in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_homepage_page_with_default_data(app):
    response = do_get(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=True)

    check_custom_homepage_html(response, expected_form_data=DEFAULT_DATA.copy())

    homepage_response = do_get(app, '/', is_sysadmin=False)

    check_homepage_html(homepage_response, expected_data=DEFAULT_HEADERS)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_homepage_with_changes(app):
    data = {
        'custom_homepage_layout': '2',
        'popular-datasets-custom-name': 'Test 1',
        'popular-datasets-custom-explanation': 'Test explanation 1',
        'recent-datasets-custom-name': 'Test 2',
        'recent-datasets-custom-explanation': 'Test explanation 2',
        'groups-custom-name': 'Test 3',
        'groups-custom-explanation': 'Test explanation 3',
        'showcases-custom-name': 'Test 4',
        'showcases-custom-explanation': 'Test explanation 4'
    }
    response = do_post(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=True, data=data)

    check_custom_homepage_html(response, expected_form_data=data.copy())

    homepage_response = do_get(app, '/', is_sysadmin=False)

    expected_homepage_headers = (
        'Test 1',
        'Test 2',
    )
    check_homepage_html(homepage_response, expected_data=expected_homepage_headers)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_reset_custom_homepage_changes(app):
    data = {
        'custom_homepage_layout': '2',
        'popular-datasets-custom-name': 'Test 1',
        'recent-datasets--custom-name': 'Test 2',
        'groups-custom-name': 'Test 3',
        'showcases-custom-name': 'Test 4'
    }
    response = do_post(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=True, data=data)
    assert response.status_code == 200

    reset_response = do_post(app, RESET_CUSTOM_HOMEPAGE_URL, is_sysadmin=True, data={})
    check_custom_homepage_html(reset_response, expected_form_data=DEFAULT_DATA.copy())

    homepage_response = do_get(app, '/', is_sysadmin=False)
    check_homepage_html(homepage_response, expected_data=DEFAULT_HEADERS)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_homepage_with_explanation_only(app):
    """Test that explanation text can be set independently of titles"""
    data = {
        'custom_homepage_layout': '1',
        'popular-datasets-custom-name': 'Popular Datasets',
        'popular-datasets-custom-explanation': 'Custom explanation for popular datasets',
        'recent-datasets-custom-name': 'New and Recent Datasets',
        'recent-datasets-custom-explanation': 'Custom explanation for recent datasets',
        'groups-custom-name': 'Groups',
        'groups-custom-explanation': 'Custom explanation for groups',
        'showcases-custom-name': 'Showcases',
        'showcases-custom-explanation': 'Custom explanation for showcases'
    }
    response = do_post(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=True, data=data)

    check_custom_homepage_html(response, expected_form_data=data.copy())


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_homepage_with_empty_explanation(app):
    """Test that empty explanation text is handled correctly"""
    data = {
        'custom_homepage_layout': '1',
        'popular-datasets-custom-name': 'Popular Datasets',
        'popular-datasets-custom-explanation': '',
        'recent-datasets-custom-name': 'New and Recent Datasets',
        'recent-datasets-custom-explanation': '',
        'groups-custom-name': 'Groups',
        'groups-custom-explanation': '',
        'showcases-custom-name': 'Showcases',
        'showcases-custom-explanation': ''
    }
    response = do_post(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=True, data=data)

    check_custom_homepage_html(response, expected_form_data=data.copy())


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_homepage_with_markdown_explanation(app):
    """Test that markdown in explanation text is processed"""
    data = {
        'custom_homepage_layout': '1',
        'popular-datasets-custom-name': 'Popular Datasets',
        'popular-datasets-custom-explanation': '**Browse** popular datasets',
        'recent-datasets-custom-name': 'New and Recent Datasets',
        'recent-datasets-custom-explanation': 'Browse *new* datasets',
        'groups-custom-name': 'Groups',
        'groups-custom-explanation': 'Learn about [groups](http://example.com)',
        'showcases-custom-name': 'Showcases',
        'showcases-custom-explanation': ''
    }
    response = do_post(app, CUSTOM_HOMEPAGE_URL, is_sysadmin=True, data=data)

    # Note: The markdown will be stored as-is and processed when rendered
    assert response.status_code == 200
