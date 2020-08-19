from abc import abstractmethod, ABCMeta

__all__ = ['CustomNamingProcessor']


class BaseNaming:
    __metaclass__ = ABCMeta
    name = None
    position = 0

    @abstractmethod
    def get_form_name(self):
        raise NotImplementedError

    @abstractmethod
    def get_default_name(self):
        raise NotImplementedError

    def parse_name_from_form(self, data):
        self.name = data.get(self.get_form_name()) or None

    def get_name(self):
        return self.name or self.get_default_name()


class GroupsNaming(BaseNaming):
    def get_form_name(self):
        return "groups-custom-name"

    def get_default_name(self):
        return "Groups"


class ShowcaseNaming(BaseNaming):
    def get_form_name(self):
        return "showcase-custom-name"

    def get_default_name(self):
        return "Showcases"


class PopularDatasetsNaming(BaseNaming):
    def get_form_name(self):
        return "datasets-popular-custom-name"

    def get_default_name(self):
        return "Popular Datasets"


class RecentDatasetsNaming(BaseNaming):
    def get_form_name(self):
        return "datasets-recent-custom-name"

    def get_default_name(self):
        return "New and Recent Datasets"


class CustomNamingProcessor:

    def __init__(self):
        self.groups = GroupsNaming()
        self.showcase = ShowcaseNaming()
        self.popular_datasets = PopularDatasetsNaming()
        self.recent_datasets = RecentDatasetsNaming()

        self.naming_processors = [
            self.groups,
            self.showcase,
            self.popular_datasets,
            self.recent_datasets
        ]
        self.add_position_to_processors()

    def add_position_to_processors(self):
        for i, processor in enumerate(self.naming_processors):
            processor.position = i

    def get_custom_naming(self, data):
        result = {}
        for processor in self.naming_processors:
            processor.parse_name_from_form(data)
            result[processor.get_form_name()] = {
                "title": processor.get_default_name(),
                "value": processor.get_name(),
                "position": processor.position,
            }
        return result
