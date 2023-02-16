import pytest

from ckanext.opendata_theme.tests.helpers import do_get, do_post

CUSTOM_FOOTER_URL = "/ckan-admin/custom_footer/"
RESET_CUSTOM_FOOTER_URL = "/ckan-admin/reset_custom_footer/"


def check_custom_footer_page_html(response, layout_type, content_0, content_1):
    assert response, 'Response is empty.'
    assert '<option value="{}" selected="selected">'.format(layout_type) in response, 'Selected wrong layout type.'
    assert content_0 in response, 'Content 1 field has unexpected content.'
    assert content_1 in response, 'Content 2 field has unexpected content.'


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_footer_page_with_not_sysadmin_user(app):
    response = do_get(app, CUSTOM_FOOTER_URL, is_sysadmin=False)
    assert '<h1>403 Forbidden</h1>' in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_footer_page(app):
    response = do_get(app, CUSTOM_FOOTER_URL, is_sysadmin=True)
    assert 2 == response.body.count('data-module="ckedit"')


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_reset_custom_footer_page(app):
    response = do_get(app, RESET_CUSTOM_FOOTER_URL, is_sysadmin=True)
    expected_data = {
        'layout_type': 'default',
        'content_0': '',
        'content_1': ''
    }
    check_custom_footer_page_html(response, **expected_data)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_empty_custom_footer_form(app):
    data = {
        'layout_type': 'custom',
        'content_0': '',
        'content_1': ''
    }
    response = do_post(app, CUSTOM_FOOTER_URL, data, is_sysadmin=True)
    check_custom_footer_page_html(response, **data)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_full_custom_footer_form(app):
    data = {
        'layout_type': 'custom',
        'content_0': 'content 1',
        'content_1': 'content 2'
    }
    response = do_post(app, CUSTOM_FOOTER_URL, data, is_sysadmin=True)
    check_custom_footer_page_html(response, **data)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_footer_form_with_forbidden_html_tags(app):
    data = {
        'layout_type': 'custom',
        'content_0': '<iframe src="https://www.w3schools.com" title="Iframe></iframe><script></script>',
        'content_1': '<form action="/action.php" method="get"><input type="submit" value=""></form>'
    }
    expected_contents = {
        'layout_type': 'custom',
        'content_0': '',
        'content_1': '&lt;form action="/action.php" method="get"&gt;&lt;input type="submit" value=""&gt;&lt;/form&gt;',
    }
    response = do_post(app, CUSTOM_FOOTER_URL, data, is_sysadmin=True)
    check_custom_footer_page_html(response, **expected_contents)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_reset_custom_footer_form_after_some_footer_modification(app):
    data = {
        'layout_type': 'custom',
        'content_0': 'content 1',
        'content_1': 'content 2'
    }
    response = do_post(app, CUSTOM_FOOTER_URL, data, is_sysadmin=True)
    check_custom_footer_page_html(response, **data)

    reset_response = do_post(app, RESET_CUSTOM_FOOTER_URL, data={}, is_sysadmin=True)
    expected_data = {
        'layout_type': 'default',
        'content_0': '',
        'content_1': ''
    }
    check_custom_footer_page_html(reset_response, **expected_data)
