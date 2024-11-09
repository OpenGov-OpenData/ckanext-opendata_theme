import pytest

from ckanext.opendata_theme.base.helpers import (
    abbreviate_name, is_data_dict_active,
    get_group_alias, get_organization_alias,
    version_builder, check_characters,
    sanityze_all_html
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
