import pytest
from unittest import mock

from ckanext.opendata_theme.base.helpers import (
    abbreviate_name, is_data_dict_active,
    get_group_alias, get_organization_alias,
    version_builder, check_characters,
    sanityze_all_html,
    get_footer_script_snippet,
    get_custom_name,
    get_custom_explanation
)
from packaging.version import InvalidVersion


def test_abbreviate_name():
    assert abbreviate_name('John Smith') == 'JS'
    assert abbreviate_name('test') == 'T'


def test_is_data_dict_active():
    assert is_data_dict_active([{'info': {'label': 'test'}}])
    assert is_data_dict_active([{'info': {'notes': 'test'}}])
    assert is_data_dict_active([{'info': {'label': 'test', 'notes': 'test'}}])
    assert not is_data_dict_active([{'info': {}}])
    assert not is_data_dict_active([{}])
    assert not is_data_dict_active([])


def test_get_group_alias():
    assert get_group_alias() == 'Group'


def test_get_organization_alias():
    assert get_organization_alias() == 'Organization'


def test_version_builder_positive():
    assert version_builder('2.7') < version_builder('2.9')
    assert version_builder('2.7.0') < version_builder('2.7.3')
    assert version_builder('2.7.3') < version_builder('2.7.12')
    assert version_builder('2.7.3') < version_builder('2.9.11')
    assert version_builder('2.7.12') < version_builder('2.9.11')
    assert version_builder('2.9.11') < version_builder('2.10.0')
    assert version_builder('2.9.11') < version_builder('2.11.0')


def test_version_builder_failed_to_build():
    with pytest.raises(InvalidVersion):
        assert version_builder('1.3.xy123')


def test_check_characters():
    assert check_characters('') is False


def test_sanityze_all_html():
    assert sanityze_all_html('<script>alert("test")</script>') == '&lt;script&gt;alert("test")&lt;/script&gt;'
    assert sanityze_all_html('<a href="test">test</a>') == '&lt;a href="test"&gt;test&lt;/a&gt;'
    assert sanityze_all_html('test') == 'test'


def test_invalid_get_footer_script_snippet():
    assert get_footer_script_snippet() is False


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_name_with_no_config(mock_get_action):
    """Test get_custom_name returns default when no config exists"""
    mock_get_action.return_value.return_value = None
    result = get_custom_name('groups-custom-name', 'Default Groups')
    assert result == 'Default Groups'


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_name_with_missing_key(mock_get_action):
    """Test get_custom_name returns default when key is missing"""
    mock_get_action.return_value.return_value = str({
        'other-key': {'title': 'Other', 'value': 'Other Value'}
    })
    result = get_custom_name('groups-custom-name', 'Default Groups')
    assert result == 'Default Groups'


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.h.markdown_extract')
@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_name_with_valid_config(mock_get_action, mock_markdown_extract):
    """Test get_custom_name returns custom value when config exists"""
    mock_get_action.return_value.return_value = str({
        'groups-custom-name': {'title': 'Groups Title', 'value': 'Custom Groups'}
    })
    mock_markdown_extract.return_value = 'Custom Groups'
    result = get_custom_name('groups-custom-name', 'Default Groups')
    assert result == 'Custom Groups'
    mock_markdown_extract.assert_called_once_with('Custom Groups')


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_explanation_with_no_config(mock_get_action):
    """Test get_custom_explanation returns default when no config exists"""
    mock_get_action.return_value.return_value = None
    result = get_custom_explanation('groups-custom-explanation', 'Default explanation text')
    assert result == 'Default explanation text'


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_explanation_with_empty_default(mock_get_action):
    """Test get_custom_explanation returns empty string when no config and no default"""
    mock_get_action.return_value.return_value = None
    result = get_custom_explanation('showcases-custom-explanation')
    assert result == ''


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_explanation_with_missing_key(mock_get_action):
    """Test get_custom_explanation returns default when key is missing"""
    mock_get_action.return_value.return_value = str({
        'other-key': {'title': 'Other', 'value': 'Other Value'}
    })
    result = get_custom_explanation('groups-custom-explanation', 'Default explanation')
    assert result == 'Default explanation'


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.h.markdown_extract')
@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_explanation_with_valid_config(mock_get_action, mock_markdown_extract):
    """Test get_custom_explanation returns custom value when config exists"""
    mock_get_action.return_value.return_value = str({
        'groups-custom-explanation': {
            'title': 'Groups Explanation',
            'value': 'This is a custom explanation text'
        }
    })
    mock_markdown_extract.return_value = 'This is a custom explanation text'
    result = get_custom_explanation('groups-custom-explanation', 'Default explanation')
    assert result == 'This is a custom explanation text'
    mock_markdown_extract.assert_called_once_with('This is a custom explanation text')


@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.h.markdown_extract')
@mock.patch('ckanext.opendata_theme.base.helpers.toolkit.get_action')
def test_get_custom_explanation_with_markdown(mock_get_action, mock_markdown_extract):
    """Test get_custom_explanation processes markdown correctly"""
    mock_get_action.return_value.return_value = str({
        'popular-datasets-custom-explanation': {
            'title': 'Popular Datasets Explanation',
            'value': '**Browse** popular datasets'
        }
    })
    mock_markdown_extract.return_value = 'Browse popular datasets'
    result = get_custom_explanation('popular-datasets-custom-explanation', '')
    assert result == 'Browse popular datasets'
    mock_markdown_extract.assert_called_once_with('**Browse** popular datasets')
