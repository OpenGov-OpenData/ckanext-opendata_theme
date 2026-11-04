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


@pytest.mark.usefixtures('with_plugins', 'clean_db')
@pytest.mark.ckan_config(
    "ckan.plugins",
    "datastore opengov_custom_theme opengov_custom_css opengov_custom_homepage "
    "opengov_custom_header opengov_custom_footer",
)
class TestDataDictionaryForm(object):

    def test_dictionary_form_lists_all_type_overrides(self, app):
        user = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset["id"])
        helpers.call_action(
            "datastore_create",
            resource_id=resource["id"],
            force=True,
            fields=[{"id": "event_date", "type": "text", "info": {"type_override": "date"}}],
            records=[{"event_date": "2024-03-15"}],
        )

        response = app.get(
            f'/dataset/{dataset["name"]}/dictionary/{resource["id"]}',
            extra_environ={"Authorization": str(user["apikey"])},
        )
        body = response.get_data(as_text=True)
        for value, label in [
            ("text", "Text"),
            ("numeric", "Numeric"),
            ("timestamp", "Timestamp"),
            ("date", "Date"),
            ("time", "Time"),
        ]:
            assert f'<option value="{value}"' in body
            assert f">{label}</option>" in body
        assert '<option value="date" selected>Date</option>' in body
