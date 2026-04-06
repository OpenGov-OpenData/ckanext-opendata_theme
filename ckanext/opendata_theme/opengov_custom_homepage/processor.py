from ckanext.opendata_theme.base.processor import AbstractParser

__all__ = ["custom_naming_processor"]


class GroupsNaming(AbstractParser):
    form_name = "groups-custom-name"
    title = "Groups Section Title"
    _default_value = "Groups"


class GroupsExplanation(AbstractParser):
    form_name = "groups-custom-explanation"
    title = "Groups Section Explanation"
    _default_value = "As datasets are published, they are grouped into categories so you can learn about popular topics."


class ShowcasesNaming(AbstractParser):
    form_name = "showcases-custom-name"
    title = "Showcases Section Title"
    _default_value = "Showcases"


class ShowcasesExplanation(AbstractParser):
    form_name = "showcases-custom-explanation"
    title = "Showcases Section Explanation"
    _default_value = ""


class PopularDatasetsNaming(AbstractParser):
    form_name = "popular-datasets-custom-name"
    title = "Popular Datasets Section Title"
    _default_value = "Popular Datasets"


class PopularDatasetsExplanation(AbstractParser):
    form_name = "popular-datasets-custom-explanation"
    title = "Popular Datasets Section Explanation"
    _default_value = "Browse popular datasets below and see what other citizens find interesting."


class RecentDatasetsNaming(AbstractParser):
    form_name = "recent-datasets-custom-name"
    title = "Recent Datasets Section Title"
    _default_value = "New and Recent Datasets"


class RecentDatasetsExplanation(AbstractParser):
    form_name = "recent-datasets-custom-explanation"
    title = "Recent Datasets Section Explanation"
    _default_value = "Browse new or modified datasets below. Click to view details or explore content."


class CustomNamingProcessor:

    def __init__(self):
        self.groups = GroupsNaming()
        self.groups_explanation = GroupsExplanation()
        self.showcases = ShowcasesNaming()
        self.showcases_explanation = ShowcasesExplanation()
        self.popular_datasets = PopularDatasetsNaming()
        self.popular_datasets_explanation = PopularDatasetsExplanation()
        self.recent_datasets = RecentDatasetsNaming()
        self.recent_datasets_explanation = RecentDatasetsExplanation()

        self.naming_processors = (
            self.groups,
            self.groups_explanation,
            self.showcases,
            self.showcases_explanation,
            self.popular_datasets,
            self.popular_datasets_explanation,
            self.recent_datasets,
            self.recent_datasets_explanation
        )

    def get_custom_naming(self, data):
        result = {}
        for processor in self.naming_processors:
            processor.parse_form_data(data)
            result[processor.form_name] = {
                "title": processor.title,
                "value": processor.value,
            }
        return result


custom_naming_processor = CustomNamingProcessor()
