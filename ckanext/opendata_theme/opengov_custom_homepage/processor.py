from ckanext.opendata_theme.base.processor import AbstractParser

__all__ = ["custom_naming_processor"]


class GroupsNaming(AbstractParser):
    form_name = "groups-custom-name"
    _default_value = "Groups"


class ShowcaseNaming(AbstractParser):
    form_name = "showcase-custom-name"
    _default_value = "Showcases"


class PopularDatasetsNaming(AbstractParser):
    form_name = "datasets-popular-custom-name"
    _default_value = "Popular Datasets"


class RecentDatasetsNaming(AbstractParser):
    form_name = "datasets-recent-custom-name"
    _default_value = "New and Recent Datasets"


class CustomNamingProcessor:

    def __init__(self):
        self.groups = GroupsNaming()
        self.showcase = ShowcaseNaming()
        self.popular_datasets = PopularDatasetsNaming()
        self.recent_datasets = RecentDatasetsNaming()

        self.naming_processors = (
            self.groups,
            self.showcase,
            self.popular_datasets,
            self.recent_datasets
        )

    def get_custom_naming(self, data):
        result = {}
        for processor in self.naming_processors:
            processor.parse_form_data(data)
            result[processor.form_name] = {
                "title": processor.default_value,
                "value": processor.value,
            }
        return result


custom_naming_processor = CustomNamingProcessor()
