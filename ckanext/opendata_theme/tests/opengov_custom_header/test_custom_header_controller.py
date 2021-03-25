import pytest
from ckan.logic import NotAuthorized

from ckanext.opendata_theme.tests.helpers import do_get, do_post

CUSTOM_HEADER_URL = "/ckan-admin/custom_header/"
RESET_CUSTOM_HEADER_URL = "/ckan-admin/reset_custom_header/"
ADD_LINK_TO_HEADER_URL = "/ckan-admin/add_link_to_header/"
REMOVE_LINK_FROM_HEADER_URL = "/ckan-admin/remove_link_from_header/"
DEFAULT_LINKS = (
    {'position': 0, 'title': 'datasets', 'link': '/dataset/'},
    {'position': 1, 'title': 'organizations', 'link': '/organization/'},
    {'position': 2, 'title': 'groups', 'link': '/group/'},
    {'position': 3, 'title': 'about', 'link': '/about'},
)
DEFAULT_HEADERS = (
    {'title': 'datasets', 'link': '/dataset/'},
    {'title': 'organizations', 'link': '/organization/'},
    {'title': 'groups', 'link': '/group/'},
    {'title': 'about', 'link': '/about'},
)


def check_custom_header_page_html(response, links, headers, default_layout=True, errors=()):
    assert response, 'Response is empty.'
    if default_layout:
        assert 'value="default" checked' in response
    else:
        assert 'value="compressed" checked' in response
    for link in links:
        assert '<div class="row" id="{}">'.format(link.get('position')) in response
        assert 'name="position" value="{}"'.format(link.get('position')) in response
        assert 'name="title" value="{}"'.format(link.get('title')) in response
        assert 'name="link" value="{}"'.format(link.get('link')) in response
    for header in headers:
        assert '<li><a href="{}">{}</a></li>'.format(header.get('link'), header.get('title')) in response
    if errors:
        for error_message in errors:
            assert error_message in response
    else:
        assert 'alert' not in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_header_page_with_not_sysadmin_user(app):
    with pytest.raises(NotAuthorized):
        do_get(app, CUSTOM_HEADER_URL, is_sysadmin=False)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_header_page(app):
    response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(response, links=[], headers=DEFAULT_HEADERS, default_layout=True)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_add_link_to_custom_header(app):
    title = 'example'
    link = 'https://example.com'
    data = {
        'new_title': title,
        'new_link': link,
    }
    expected_links = [
        {'position': 4, 'title': title, 'link': link},
    ]
    expected_links.extend(DEFAULT_LINKS)

    expected_headers = [
        {'title': title, 'link': link},
    ]
    expected_headers.extend(DEFAULT_HEADERS)

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=DEFAULT_HEADERS, default_layout=True)

    response = do_post(app, ADD_LINK_TO_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_add_unsupported_link_to_custom_header(app):
    title = 'example'
    link = 'http://example.com'
    data = {
        'new_title': title,
        'new_link': link,
    }
    expected_links = [
        {'position': 4, 'title': title, 'link': link},
    ]
    expected_links.extend(DEFAULT_LINKS)

    expected_headers = list(DEFAULT_HEADERS)

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=expected_headers, default_layout=True)

    response = do_post(app, ADD_LINK_TO_HEADER_URL, data, is_sysadmin=True)
    expected_error_messages = [
        'Ckanext.opendata theme.custom header.data: Only HTTPS urls supported &#34;{}&#34;'.format(link)
    ]
    check_custom_header_page_html(response,
                                  links=expected_links,
                                  headers=expected_headers,
                                  errors=expected_error_messages)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_remove_link_to_custom_header(app):
    data = {
        'to_remove': 'about',
    }
    expected_links = list(DEFAULT_LINKS)

    expected_links.pop(3)

    expected_headers = list(DEFAULT_HEADERS)
    expected_headers.pop(3)

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=expected_headers, default_layout=True)

    response = do_post(app, REMOVE_LINK_FROM_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers)
    assert 'about' not in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_update_multiple_custom_header_links(app):
    data = {
        'layout_type': 'default',
        'link': ['/dataset/', '/organization/', '/group/', '/about'],
        'position': ['3', '2', '1', '0'],
        'title': ['datasets updated', 'organizations updated', 'groups updated', 'about']
    }
    expected_links = (
        {'position': 3, 'title': 'datasets updated', 'link': '/dataset/'},
        {'position': 2, 'title': 'organizations updated', 'link': '/organization/'},
        {'position': 1, 'title': 'groups updated', 'link': '/group/'},
        {'position': 0, 'title': 'about', 'link': '/about'},
    )
    expected_headers = (
        {'title': 'datasets updated', 'link': '/dataset/'},
        {'title': 'organizations updated', 'link': '/organization/'},
        {'title': 'groups updated', 'link': '/group/'},
        {'title': 'about', 'link': '/about'},
    )

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=list(DEFAULT_HEADERS), default_layout=True)

    response = do_post(app, CUSTOM_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_update_single_custom_header_links(app):
    data = {
        'layout_type': 'compressed',
        'link': '/dataset/',
        'position': '0',
        'title': 'datasets updated',
    }
    expected_links = (
        {'position': 0, 'title': 'datasets updated', 'link': '/dataset/'},
    )
    expected_headers = (
        {'title': 'datasets updated', 'link': '/dataset/'},
    )

    custom_header_response = do_get(app, CUSTOM_HEADER_URL, is_sysadmin=True)
    check_custom_header_page_html(custom_header_response, links=[], headers=list(DEFAULT_HEADERS), default_layout=True)

    response = do_post(app, CUSTOM_HEADER_URL, data, is_sysadmin=True)
    check_custom_header_page_html(response, links=expected_links, headers=expected_headers, default_layout=False)
