import pytest

from ckanext.opendata_theme.tests.helpers import do_get, do_post

CUSTOM_HEADER_URL = "/ckan-admin/custom_header/"
RESET_CUSTOM_HEADER_URL = "/ckan-admin/reset_custom_header/"
ADD_LINK_TO_HEADER_URL = "/ckan-admin/add_link_to_header/"
REMOVE_LINK_FROM_HEADER_URL = "/ckan-admin/remove_link_from_header/"
DEFAULT_LINKS = (
    {'position': 0, 'title': 'Datasets', 'url': '/dataset/'},
    {'position': 1, 'title': 'Organizations', 'url': '/organization/'},
    {'position': 2, 'title': 'Groups', 'url': '/group/'}
)
DEFAULT_HEADERS = (
    {'title': 'Datasets', 'url': '/dataset/'},
    {'title': 'Organizations', 'url': '/organization/'},
    {'title': 'Groups', 'url': '/group/'}
)


def check_custom_header_page_html(response, links, headers, default_layout=True):
    assert response, 'Response is empty.'
    if default_layout:
        assert '<option value="default" selected="selected">' in response
    else:
        assert '<option value="compressed" selected="selected">' in response
    for link in links:
        assert '<div class="row" id="{}">'.format(link.get('position')) in response
        assert 'name="position" value="{}"'.format(link.get('position')) in response
        assert 'name="title" value="{}"'.format(link.get('title')) in response
        assert 'name="url" value="{}"'.format(link.get('url')) in response
    for header in headers:
        assert '<li><a href="{}">{}</a></li>'.format(header.get('url'), header.get('title')) in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_header_page_with_not_sysadmin_user(app):
    response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=False)
    assert '<h1>403 Forbidden</h1>' in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_header_page(app):
    response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(response, links=[], headers=DEFAULT_HEADERS, default_layout=True)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_add_link_to_custom_header(app):
    title = 'example'
    url = 'https://example.com'
    data = {
        'new_title': title,
        'new_url': url,
    }
    expected_links = [
        {'position': 3, 'title': title, 'url': url},
    ]
    expected_links.extend(DEFAULT_LINKS)

    expected_headers = [
        {'title': title, 'url': url},
    ]
    expected_headers.extend(DEFAULT_HEADERS)

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=DEFAULT_HEADERS, default_layout=True)

    response = do_post(app, ADD_LINK_TO_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_add_unsupported_link_to_custom_header(app):
    title = 'example'
    url = 'http://example.com'
    data = {
        'new_title': title,
        'new_link': url
    }
    response = do_post(app, ADD_LINK_TO_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response,
                                  links=[],
                                  headers=DEFAULT_HEADERS)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_remove_link_to_custom_header(app):
    data = {
        'to_remove': 'Groups',
    }
    expected_links = list(DEFAULT_LINKS)

    expected_links.pop(2)

    expected_headers = list(DEFAULT_HEADERS)
    expected_headers.pop(2)

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=expected_headers, default_layout=True)

    response = do_post(app, REMOVE_LINK_FROM_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers)
    assert 'Groups' not in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_update_multiple_custom_header_links(app):
    data = {
        'layout_type': 'default',
        'position': ['2', '1', '0'],
        'title': ['Datasets Updated', 'Organizations Updated', 'Groups Updated'],
        'url': ['/dataset/', '/organization/', '/group/']
    }
    expected_links = (
        {'position': 2, 'title': 'Datasets Updated', 'url': '/dataset/'},
        {'position': 1, 'title': 'Organizations Updated', 'url': '/organization/'},
        {'position': 0, 'title': 'Groups Updated', 'url': '/group/'}
    )
    expected_headers = (
        {'title': 'Datasets Updated', 'url': '/dataset/'},
        {'title': 'Organizations Updated', 'url': '/organization/'},
        {'title': 'Groups Updated', 'url': '/group/'}
    )

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=list(DEFAULT_HEADERS), default_layout=True)

    response = do_post(app, CUSTOM_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_update_single_custom_header_links(app):
    data = {
        'layout_type': 'compressed',
        'position': '0',
        'title': 'Datasets Updated',
        'url': '/dataset/'
    }
    expected_headers = [
        {'title': 'Datasets Updated', 'url': '/dataset/'}
    ]

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=DEFAULT_HEADERS, default_layout=True)

    response = do_post(app, CUSTOM_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=[], headers=expected_headers, default_layout=False)
