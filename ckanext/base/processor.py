import abc


class AbstractParser(object):
    __metaclass__ = abc.ABCMeta
    class_name = ''
    form_name = ''
    title = ''
    location = ''
    color = ''
    _default_color = ''

    @classmethod
    def get_css_from_data(cls, data):
        cls.parse_form_data(data)
        if cls.color:
            return {cls.location: cls.color.encode('utf-8')}

    @classmethod
    def parse_form_data(cls, data):
        value = data.get(cls.form_name, cls._default_color)
        cls.color = value
