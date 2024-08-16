import pytest

from ckanext.opendata_theme.base import helpers
from packaging.version import InvalidVersion
from ckan.common import config

from unittest.mock import patch


def test_version_builder_positive():
    assert helpers.version_builder('2.7') < helpers.version_builder('2.9')
    assert helpers.version_builder('2.7.0') < helpers.version_builder('2.7.3')
    assert helpers.version_builder('2.7.3') < helpers.version_builder('2.7.12')
    assert helpers.version_builder('2.7.3') < helpers.version_builder('2.9.0')
    assert helpers.version_builder('2.7.3') < helpers.version_builder('2.9.7')
    assert helpers.version_builder('2.7.12') < helpers.version_builder('2.9.0')
    assert helpers.version_builder('2.7.12') < helpers.version_builder('2.9.7')
    assert helpers.version_builder('2.7.12') < helpers.version_builder('2.10.0')


def test_version_builder_failed_to_build():
    with pytest.raises(InvalidVersion):
        assert helpers.version_builder('1.3.xy123')


def test_get_segment_writekey(self):
    config['ckan.segment_writekey'] = "loremipsum"
    writekey = helpers.get_segment_writekey()
    assert writekey == "loremipsum"


# Mock objects
class MockUser:
    def __init__(self, email):
        self.email = email


class MockUserToken:
    def __init__(self, platform_uuid):
        self.platform_uuid = platform_uuid


# Test cases
def test_get_user_uuid_no_user():
    with patch('helpers.c.user', None):
        assert helpers.get_user_uuid() is None


def test_get_user_uuid_no_token():
    mock_user = MockUser(email='test@example.com')
    with patch('helpers.c.user', mock_user), \
         patch('helpers.c.userobj', mock_user), \
         patch('helpers.model.Session.query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        assert helpers.get_user_uuid() is None


def test_get_user_uuid_with_token():
    mock_user = MockUser(email='test@example.com')
    mock_token = MockUserToken(platform_uuid='1234-5678')
    with patch('helpers.c.user', mock_user), \
         patch('helpers.c.userobj', mock_user), \
         patch('helpers.model.Session.query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_token
        assert helpers.get_user_uuid() == '1234-5678'


def test_get_user_uuid_exception():
    mock_user = MockUser(email='test@example.com')
    with patch('helpers.c.user', mock_user), \
         patch('helpers.c.userobj', mock_user), \
         patch('helpers.model.Session.query') as mock_query:
        mock_query.side_effect = Exception("Database error")
        assert helpers.get_user_uuid() is None
