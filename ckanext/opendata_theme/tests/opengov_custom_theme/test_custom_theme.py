import pytest
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.opendata_theme.opengov_custom_theme.utils import dictionary_filename


@pytest.mark.usefixtures('with_plugins', 'clean_db')
@pytest.mark.ckan_config("ckan.plugins", "datastore opengov_custom_theme")
class TestDataDictionaryDownload(object):

    def test_data_dictionary_download_basic(self, app):
        resource = factories.Resource()
        data = {
            "resource_id": resource["id"],
            "force": True,
            "records": [{u"book": "annakarenina"}, {u"book": "warandpeace"}],
        }
        helpers.call_action("datastore_create", **data)

        response = app.get(f'/datastore/dictionary_download/{resource["id"]}')
        assert (
            "column,type,label,description\r\n"
            "book,text,,\r\n" == response.get_data(as_text=True)
        )

    def test_data_dictionary_download_filename_uses_slugified_name(self, app):
        resource = factories.Resource(name="My Great Data!")
        data = {
            "resource_id": resource["id"],
            "force": True,
            "records": [{u"book": "annakarenina"}],
        }
        helpers.call_action("datastore_create", **data)

        response = app.get(f'/datastore/dictionary_download/{resource["id"]}')
        assert (
            'filename="my-great-data-data-dictionary.csv"'
            in response.headers["Content-disposition"]
        )

    def test_dictionary_filename_falls_back_to_resource_id(self):
        # An unknown resource id makes resource_show raise; the filename should
        # fall back to the raw resource id rather than error out.
        assert (
            dictionary_filename("does-not-exist")
            == "does-not-exist-data-dictionary.csv"
        )
