import json
from types import SimpleNamespace
from unittest import mock

import pytest

import ckan.plugins.toolkit as toolkit

import ckanext.opendata_theme.opengov_custom_search_filter.helpers as helper
from ckanext.opendata_theme.opengov_custom_search_filter.constants import (
    DEFAULT_RESOURCE_TYPE_CATEGORIES,
    RESOURCE_TYPE_FILTER_ENABLED_KEY,
)
import ckanext.opendata_theme.opengov_custom_search_filter.plugin as plugin_module
from ckanext.opendata_theme.opengov_custom_search_filter.plugin import OpenDataThemeSearchFilterPlugin

VALID = {'tabular': {'label': 'Tabular Data', 'enabled': True, 'formats': ['CSV', 'XLS']}}


def _with(**overrides):
    item = dict(VALID['tabular'], **overrides)
    return {'tabular': item}


class TestValidator(object):
    def test_accepts_dict(self):
        assert helper.resource_type_categories_validator(VALID) == VALID

    def test_accepts_json_string(self):
        assert helper.resource_type_categories_validator(json.dumps(VALID)) == VALID

    def test_accepts_shipped_defaults(self):
        helper.resource_type_categories_validator(DEFAULT_RESOURCE_TYPE_CATEGORIES)

    @pytest.mark.parametrize('value', ['', '   ', '\n'])
    def test_rejects_blank(self, value):
        with pytest.raises(toolkit.Invalid):
            helper.resource_type_categories_validator(value)

    @pytest.mark.parametrize('value', ['not json', '{"a": ', '[]', '"text"', '42'])
    def test_rejects_invalid_json_or_non_object(self, value):
        with pytest.raises(toolkit.Invalid):
            helper.resource_type_categories_validator(value)

    @pytest.mark.parametrize('key', ['Bad Key', 'UPPER', 'has/slash', 'a&b=c', ''])
    def test_rejects_bad_category_key(self, key):
        with pytest.raises(toolkit.Invalid):
            helper.resource_type_categories_validator({key: VALID['tabular']})

    @pytest.mark.parametrize('item', [
        'not a dict',
        {'formats': ['CSV']},
        {'label': '  ', 'formats': ['CSV']},
        {'label': 5, 'formats': ['CSV']},
        {'label': 'X'},
        {'label': 'X', 'formats': []},
        {'label': 'X', 'formats': 'CSV'},
        {'label': 'X', 'formats': ['CSV', '']},
        {'label': 'X', 'formats': ['CSV', 7]},
        {'label': 'X', 'enabled': 'true', 'formats': ['CSV']},
    ])
    def test_rejects_bad_category(self, item):
        with pytest.raises(toolkit.Invalid):
            helper.resource_type_categories_validator({'tabular': item})

    def test_enabled_is_optional(self):
        value = {'tabular': {'label': 'X', 'formats': ['CSV']}}
        assert helper.resource_type_categories_validator(value) == value

    def test_format_limit(self):
        at_limit = _with(formats=['f{}'.format(i) for i in range(helper._MAX_FORMATS_PER_CATEGORY)])
        helper.resource_type_categories_validator(at_limit)

        over_limit = _with(formats=['f{}'.format(i) for i in range(helper._MAX_FORMATS_PER_CATEGORY + 1)])
        with pytest.raises(toolkit.Invalid):
            helper.resource_type_categories_validator(over_limit)


def test_escape_solr_value():
    assert helper.escape_solr_value('CSV') == 'CSV'
    assert helper.escape_solr_value('ESRI REST" OR *:*') == 'ESRI REST\\" OR *:*'
    assert helper.escape_solr_value('a\\b') == 'a\\\\b'


class TestGetResourceTypeConfig(object):
    def _call(self, raw):
        fake_g = SimpleNamespace()
        with mock.patch.object(helper, 'g', fake_g), \
                mock.patch.object(helper.toolkit, 'get_action') as get_action:
            get_action.return_value = mock.Mock(return_value=raw)
            return helper.get_resource_type_config()

    def test_never_configured_uses_defaults(self):
        assert self._call(None) == DEFAULT_RESOURCE_TYPE_CATEGORIES

    def test_explicit_empty_is_respected(self):
        assert self._call('{}') == {}

    def test_stored_value_is_used(self):
        assert self._call(str(VALID)) == VALID

    @pytest.mark.parametrize('raw', ['not python', '[1, 2]', '"text"'])
    def test_garbage_falls_back_to_defaults(self, raw):
        assert self._call(raw) == DEFAULT_RESOURCE_TYPE_CATEGORIES

    def test_result_is_cached_for_the_request(self):
        fake_g = SimpleNamespace()
        with mock.patch.object(helper, 'g', fake_g), \
                mock.patch.object(helper.toolkit, 'get_action') as get_action:
            action = mock.Mock(return_value=str(VALID))
            get_action.return_value = action
            helper.get_resource_type_config()
            helper.get_resource_type_config()
        assert action.call_count == 1


CONFIG = {
    'tabular': {'label': 'Tabular Data', 'enabled': True, 'formats': ['CSV']},
    'images': {'label': 'Images', 'enabled': False, 'formats': ['PNG']},
}


class TestCategoryHelpers(object):
    def test_formats_exclude_disabled_categories(self):
        with mock.patch.object(helper, 'get_resource_type_config', return_value=CONFIG):
            assert helper.get_resource_type_formats() == {'tabular': ['CSV']}

    @pytest.mark.parametrize('enabled', [None, '', 'false', 'False', '0'])
    def test_categories_empty_when_filter_disabled(self, enabled):
        conf = {RESOURCE_TYPE_FILTER_ENABLED_KEY: enabled}
        with mock.patch.object(helper, 'config', conf), \
                mock.patch.object(helper, 'get_resource_type_config', return_value=CONFIG):
            assert helper.get_resource_type_categories() == []

    @pytest.mark.parametrize('enabled', ['true', 'True', '1'])
    def test_categories_only_enabled_when_filter_enabled(self, enabled):
        conf = {RESOURCE_TYPE_FILTER_ENABLED_KEY: enabled}
        with mock.patch.object(helper, 'config', conf), \
                mock.patch.object(helper, 'get_resource_type_config', return_value=CONFIG):
            assert helper.get_resource_type_categories() == [{'name': 'tabular', 'label': 'Tabular Data'}]


class TestBeforeSearch(object):
    def _search(self, extras, fq=None, enabled='true', formats=None):
        formats = {'tabular': ['CSV', 'ESRI "x"']} if formats is None else formats
        params = {'extras': extras}
        if fq:
            params['fq'] = fq
        conf = {RESOURCE_TYPE_FILTER_ENABLED_KEY: enabled}
        fake_toolkit = SimpleNamespace(asbool=toolkit.asbool, config=conf)
        with mock.patch.object(plugin_module, 'toolkit', fake_toolkit), \
                mock.patch.object(helper, 'get_resource_type_formats', return_value=formats):
            return OpenDataThemeSearchFilterPlugin().before_search(params)

    def test_adds_escaped_fq(self):
        result = self._search({'ext_res_type': 'tabular'})
        assert result['fq'] == '(res_format:"CSV" OR res_format:"ESRI \\"x\\"")'

    def test_appends_to_existing_fq(self):
        result = self._search({'ext_res_type': 'tabular'}, fq='organization:foo')
        assert result['fq'].startswith('organization:foo (res_format:"CSV"')

    def test_accepts_list_value(self):
        result = self._search({'ext_res_type': ['tabular', 'images']})
        assert 'res_format:"CSV"' in result['fq']

    @pytest.mark.parametrize('extras', [{}, {'ext_res_type': ''}, {'ext_res_type': 'unknown'}])
    def test_no_filter_for_missing_or_unknown_type(self, extras):
        assert 'fq' not in self._search(extras)

    def test_no_filter_when_category_disabled_or_removed(self):
        assert 'fq' not in self._search({'ext_res_type': 'tabular'}, formats={})

    @pytest.mark.parametrize('enabled', [None, 'false'])
    def test_no_filter_when_feature_disabled(self, enabled):
        assert 'fq' not in self._search({'ext_res_type': 'tabular'}, enabled=enabled)
