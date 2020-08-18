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


class ShowcaseNaming(BaseNaming):

    def get_form_name(self):
        return "showcase-custom-name"

    def get_default_name(self):
        return "Showcase"


class PopularDatasetsNamings(BaseNaming):
    def get_form_name(self):
        return "datasets-popular-custom-name"

    def get_default_name(self):
        return "Popular Datasets"


class RecentDatasetsNamings(BaseNaming):
    def get_form_name(self):
        return "datasets-recent-custom-name"

    def get_default_name(self):
        return "New and Recent Datasets"


class GroupsNamings(BaseNaming):
    def get_form_name(self):
        return "groups-custom-name"

    def get_default_name(self):
        return "Groups"


class CustomNamingProcessor:

    def __init__(self):
        self.showcase = ShowcaseNaming()
        self.groups = GroupsNamings()
        self.popular_datasets = PopularDatasetsNamings()
        self.recent_datasets = RecentDatasetsNamings()

        self.namings_processors = [
            self.showcase,
            self.groups,
            self.popular_datasets,
            self.recent_datasets
        ]
        self.add_position_to_processors()

    def add_position_to_processors(self):
        for i, processor in enumerate(self.namings_processors):
            processor.position = i

    def get_custom_namings(self, data):
        result = {}
        for processor in self.namings_processors:
            processor.parse_name_from_form(data)
            result[processor.get_form_name()] = {
                "title": processor.get_default_name(),
                "value": processor.get_name(),
                "position": processor.position,
            }
        return result
