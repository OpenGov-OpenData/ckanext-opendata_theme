import abc


class AbstractParser(object):
    __metaclass__ = abc.ABCMeta
    class_name = ''
    form_name = ''
    title = ''
    location = ''
    value = ''
    _default_value = ''

    @property
    def default_value(self):
        return self._default_value

    @classmethod
    def get_css_from_data(cls, data):
        cls.parse_form_data(data)
        if cls.value:
            return {cls.location: cls.value.encode('utf-8')}

    @classmethod
    def parse_form_data(cls, data):
        value = data.get(cls.form_name, cls._default_value)
        cls.value = value
