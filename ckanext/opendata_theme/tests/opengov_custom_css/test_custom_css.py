import pytest
from ckan.logic import NotAuthorized

from ckanext.opendata_theme.tests.helpers import do_get, do_post

CUSTOM_CSS_URL = "/ckan-admin/custom_css/"
RESET_CUSTOM_CSS_URL = "/ckan-admin/reset_custom_css/"

DEFAULT_DATA = {
    'custom-css-account-header-background-color': '#044187',
    'custom-css-account-header-color': '#ffffff',
    'custom-css-account-hover-background-color': '#1f76d8',
    'custom-css-account-hover-navigation-button-background-color': '#044187',
    'custom-css-footer-background-color': '#383b3d',
    'custom-css-footer-color': '#ffffff',
    'custom-css-footer-link-color': '#ffffff',
    'custom-css-header-background-color': '#1f76d8',
    'custom-css-header-text-color': '#ffffff',
    'custom-css-link-color': '#131517',
    'custom-css-link-hover-color': '#165cab',
    'custom-css-module-header-background-color': '#1f76d8',
    'custom-css-module-header-color': '#ffffff',
}

DEFAULT_CUSTOM_CSS = (
    '.account-masthead {background: #044187}',
    '.account-masthead .account ul li a,.account-masthead .account ul li a:hover {color: #ffffff}',
    '.account-masthead .account ul li a:hover {background: #1f76d8}',
    '.masthead {background: #1f76d8}',
    '.navbar .nav>li>a,.masthead .nav>li>a,.masthead .nav>.active>a {color: #ffffff}',
    '.masthead .navigation .nav-pills li a:hover,.masthead .navigation .nav-pills li.active a {background-color: #044187}',
    '.module-heading {background: #1f76d8; color: #ffffff}',
    'body, .site-footer {background: #383b3d}',
    '.site-footer,.site-footer label,.site-footer small {color: #ffffff}',
    'a {color: #131517}',
    'a:hover {color: #165cab}',
    '.site-footer a,.site-footer a:hover {color: #ffffff}',
)


def check_custom_css_page_html(response, expected_form_data, expected_css_data, errors=()):
    assert response, 'Response is empty.'
    assert len(expected_form_data.keys()) == response.body.count('opendata-theme-color-picker')
    for key, value in expected_form_data.items():
        assert 'name="{0}" id="{0}" value="{1}"'.format(
            key, value) in response, 'Missed form field for "{}".'.format(key)
    for line in expected_css_data:
        assert line in response, 'CSS line "{}" missed in result html.'.format(line)
    if errors:
        for error_message in errors:
            assert error_message in response, 'Error message "{}" not in HTML.'.format(error_message)
    else:
        assert 'alert' not in response, 'Result HTML contains alerts when they are not expected.'


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_css_page_with_not_sysadmin_user(app):
    with pytest.raises(NotAuthorized):
        do_get(app, CUSTOM_CSS_URL, is_sysadmin=False)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_get_custom_css_page_with_default_data(app):
    response = do_get(app, CUSTOM_CSS_URL, is_sysadmin=True)

    check_custom_css_page_html(response, expected_form_data=DEFAULT_DATA.copy(), expected_css_data=DEFAULT_CUSTOM_CSS)


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_css_page_with_changed_color(app):
    data = DEFAULT_DATA.copy()
    data['custom-css-account-header-background-color'] = '#044189'
    unexpected_custom_css = '.account-masthead {background: #044187}'
    expected_custom_css = list(DEFAULT_CUSTOM_CSS)
    expected_custom_css.remove(unexpected_custom_css)
    expected_custom_css.append('.account-masthead {background: #044189}')
    response = do_post(app, CUSTOM_CSS_URL, is_sysadmin=True, data=data)

    check_custom_css_page_html(response, expected_form_data=data, expected_css_data=expected_custom_css)
    assert unexpected_custom_css not in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_post_custom_css_page_with_changed_color_respond_with_contrast_connected_message(app):
    data = DEFAULT_DATA.copy()
    data['custom-css-account-header-background-color'] = '#ffffff'

    unexpected_custom_css = '.account-masthead {background: #ffffff}'

    expected_custom_css = list(DEFAULT_CUSTOM_CSS)

    response = do_post(app, CUSTOM_CSS_URL, is_sysadmin=True, data=data)
    messages = [
        'Account Header Background Color and Account Header Text Color: Contrast ratio is not high enough.'
    ]
    check_custom_css_page_html(response, expected_form_data=data, expected_css_data=expected_custom_css,
                               errors=messages)
    assert unexpected_custom_css not in response


@pytest.mark.usefixtures("clean_db", "with_request_context")
def test_reset_changed_custom_css(app):
    data = DEFAULT_DATA.copy()
    data['custom-css-account-header-background-color'] = '#044189'
    unexpected_custom_css = '.account-masthead {background: #044187}'
    expected_custom_css = list(DEFAULT_CUSTOM_CSS)
    expected_custom_css.remove(unexpected_custom_css)
    expected_custom_css.append('.account-masthead {background: #044189}')
    response = do_post(app, CUSTOM_CSS_URL, is_sysadmin=True, data=data)
    assert unexpected_custom_css not in response

    reset_response = do_post(app, RESET_CUSTOM_CSS_URL, data={})
    check_custom_css_page_html(reset_response,
                               expected_form_data=DEFAULT_DATA.copy(),
                               expected_css_data=DEFAULT_CUSTOM_CSS)
