from ckanext.opendata_theme.opengov_custom_homepage.processor import (
    GroupsExplanation,
    ShowcasesExplanation,
    PopularDatasetsExplanation,
    RecentDatasetsExplanation,
    CustomNamingProcessor
)


class TestGroupsExplanation:
    """Test GroupsExplanation processor"""

    def test_default_value(self):
        processor = GroupsExplanation()
        assert processor._default_value == (
            "As datasets are published, they are grouped into categories "
            "so you can learn about popular topics."
        )

    def test_form_name(self):
        processor = GroupsExplanation()
        assert processor.form_name == "groups-custom-explanation"

    def test_title(self):
        processor = GroupsExplanation()
        assert processor.title == "Groups Section Explanation"

    def test_parse_form_data_with_custom_value(self):
        processor = GroupsExplanation()
        form_data = {'groups-custom-explanation': 'Custom explanation text'}
        processor.parse_form_data(form_data)
        assert processor.value == 'Custom explanation text'

    def test_parse_form_data_with_empty_value(self):
        processor = GroupsExplanation()
        form_data = {'groups-custom-explanation': ''}
        processor.parse_form_data(form_data)
        assert processor.value == ''


class TestShowcasesExplanation:
    """Test ShowcasesExplanation processor"""

    def test_default_value(self):
        processor = ShowcasesExplanation()
        assert processor._default_value == ""

    def test_form_name(self):
        processor = ShowcasesExplanation()
        assert processor.form_name == "showcases-custom-explanation"

    def test_title(self):
        processor = ShowcasesExplanation()
        assert processor.title == "Showcases Section Explanation"

    def test_parse_form_data_with_custom_value(self):
        processor = ShowcasesExplanation()
        form_data = {'showcases-custom-explanation': 'Custom showcase explanation'}
        processor.parse_form_data(form_data)
        assert processor.value == 'Custom showcase explanation'


class TestPopularDatasetsExplanation:
    """Test PopularDatasetsExplanation processor"""

    def test_default_value(self):
        processor = PopularDatasetsExplanation()
        assert processor._default_value == (
            "Browse popular datasets below and see what other citizens find interesting."
        )

    def test_form_name(self):
        processor = PopularDatasetsExplanation()
        assert processor.form_name == "popular-datasets-custom-explanation"

    def test_title(self):
        processor = PopularDatasetsExplanation()
        assert processor.title == "Popular Datasets Section Explanation"

    def test_parse_form_data_with_custom_value(self):
        processor = PopularDatasetsExplanation()
        form_data = {'popular-datasets-custom-explanation': 'Check out popular data'}
        processor.parse_form_data(form_data)
        assert processor.value == 'Check out popular data'


class TestRecentDatasetsExplanation:
    """Test RecentDatasetsExplanation processor"""

    def test_default_value(self):
        processor = RecentDatasetsExplanation()
        assert processor._default_value == (
            "Browse new or modified datasets below. Click to view details or explore content."
        )

    def test_form_name(self):
        processor = RecentDatasetsExplanation()
        assert processor.form_name == "recent-datasets-custom-explanation"

    def test_title(self):
        processor = RecentDatasetsExplanation()
        assert processor.title == "Recent Datasets Section Explanation"

    def test_parse_form_data_with_custom_value(self):
        processor = RecentDatasetsExplanation()
        form_data = {'recent-datasets-custom-explanation': 'See new datasets here'}
        processor.parse_form_data(form_data)
        assert processor.value == 'See new datasets here'


class TestCustomNamingProcessor:
    """Test CustomNamingProcessor with explanations"""

    def test_processor_initialization(self):
        processor = CustomNamingProcessor()
        assert processor.groups is not None
        assert processor.groups_explanation is not None
        assert processor.showcases is not None
        assert processor.showcases_explanation is not None
        assert processor.popular_datasets is not None
        assert processor.popular_datasets_explanation is not None
        assert processor.recent_datasets is not None
        assert processor.recent_datasets_explanation is not None

    def test_naming_processors_tuple_includes_all_processors(self):
        processor = CustomNamingProcessor()
        assert len(processor.naming_processors) == 8
        assert processor.groups in processor.naming_processors
        assert processor.groups_explanation in processor.naming_processors
        assert processor.showcases in processor.naming_processors
        assert processor.showcases_explanation in processor.naming_processors
        assert processor.popular_datasets in processor.naming_processors
        assert processor.popular_datasets_explanation in processor.naming_processors
        assert processor.recent_datasets in processor.naming_processors
        assert processor.recent_datasets_explanation in processor.naming_processors

    def test_get_custom_naming_with_all_fields(self):
        processor = CustomNamingProcessor()
        form_data = {
            'groups-custom-name': 'Custom Groups',
            'groups-custom-explanation': 'Custom groups explanation',
            'showcases-custom-name': 'Custom Showcases',
            'showcases-custom-explanation': 'Custom showcases explanation',
            'popular-datasets-custom-name': 'Custom Popular',
            'popular-datasets-custom-explanation': 'Custom popular explanation',
            'recent-datasets-custom-name': 'Custom Recent',
            'recent-datasets-custom-explanation': 'Custom recent explanation'
        }
        result = processor.get_custom_naming(form_data)

        assert 'groups-custom-name' in result
        assert result['groups-custom-name']['value'] == 'Custom Groups'
        assert 'groups-custom-explanation' in result
        assert result['groups-custom-explanation']['value'] == 'Custom groups explanation'

        assert 'showcases-custom-name' in result
        assert result['showcases-custom-name']['value'] == 'Custom Showcases'
        assert 'showcases-custom-explanation' in result
        assert result['showcases-custom-explanation']['value'] == 'Custom showcases explanation'

        assert 'popular-datasets-custom-name' in result
        assert result['popular-datasets-custom-name']['value'] == 'Custom Popular'
        assert 'popular-datasets-custom-explanation' in result
        assert result['popular-datasets-custom-explanation']['value'] == 'Custom popular explanation'

        assert 'recent-datasets-custom-name' in result
        assert result['recent-datasets-custom-name']['value'] == 'Custom Recent'
        assert 'recent-datasets-custom-explanation' in result
        assert result['recent-datasets-custom-explanation']['value'] == 'Custom recent explanation'

    def test_get_custom_naming_with_defaults(self):
        processor = CustomNamingProcessor()
        form_data = {}
        result = processor.get_custom_naming(form_data)

        # Check that default values are used
        assert result['groups-custom-explanation']['value'] == (
            "As datasets are published, they are grouped into categories "
            "so you can learn about popular topics."
        )
        assert result['showcases-custom-explanation']['value'] == ""
        assert result['popular-datasets-custom-explanation']['value'] == (
            "Browse popular datasets below and see what other citizens find interesting."
        )
        assert result['recent-datasets-custom-explanation']['value'] == (
            "Browse new or modified datasets below. Click to view details or explore content."
        )

    def test_get_custom_naming_with_mixed_values(self):
        processor = CustomNamingProcessor()
        form_data = {
            'groups-custom-name': 'Custom Groups',
            'groups-custom-explanation': '',  # Empty, clears the text
            'showcases-custom-name': '',
            'showcases-custom-explanation': 'Custom showcases text',  # Custom value
        }
        result = processor.get_custom_naming(form_data)

        assert result['groups-custom-name']['value'] == 'Custom Groups'
        assert result['groups-custom-explanation']['value'] == ''
        assert result['showcases-custom-name']['value'] == ''
        assert result['showcases-custom-explanation']['value'] == 'Custom showcases text'
