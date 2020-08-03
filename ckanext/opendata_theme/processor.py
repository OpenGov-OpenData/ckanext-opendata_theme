from collections import defaultdict
from abc import ABCMeta, abstractmethod

__all__ = ["custom_style_processor"]


class AbstractParser:

    @abstractmethod
    def get_css_from_data(self, data):
        return

    @abstractmethod
    def get_class_name(self):
        raise NotImplemented

    @abstractmethod
    def get_form_name(self):
        raise NotImplemented

    @abstractmethod
    def get_default_color(self):
        raise NotImplementedError

    @abstractmethod
    def get_title(self):
        raise NotImplementedError


class FooterColorJob(AbstractParser):

    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'color': value.encode('utf-8')}

    def get_class_name(self):
        return 'custom-footer'

    def get_form_name(self):
        return 'custom-css-footer-color'

    def get_title(self):
        return "Footer Text Color"

    def get_default_color(self):
        return "#ffffff"


class FooterBackGroundJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'background': value.encode('utf-8')}

    def get_class_name(self):
        return 'custom-footer'

    def get_form_name(self):
        return "custom-css-footer-background-color"

    def get_title(self):
        return "Footer Background Color"

    def get_default_color(self):
        return "#002664"


class NavigationHeaderBackGroundJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'background': value.encode('utf-8')}

    def get_class_name(self):
        return '.masthead'

    def get_form_name(self):
        return "custom-css-header-background-color"

    def get_title(self):
        return "Footer Background Color"

    def get_default_color(self):
        return "#002664"


class NavigationHeaderColorJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'color': value.encode('utf-8')}

    def get_class_name(self):
        return '.masthead'

    def get_form_name(self):
        return "custom-css-header-background-color"

    def get_default_color(self):
        return "#002664"

    def get_title(self):
        return "Navigation Header Text color"


class ModuleHeaderColorJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'color': value.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return "custom-css-module-header-color"

    def get_default_color(self):
        return "#ffffff"

    def get_title(self):
        return "Side Menu header text color"


class ModuleHeaderBackgroundColorJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'background': value.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return "custom-css-module-header-background-color"

    def get_default_color(self):
        return "#002664"

    def get_title(self):
        return "Side Menu header background color"


class AccountHoverBackgroundColorJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'background': value.encode('utf-8')}

    def get_class_name(self):
        return '.account-masthead .account ul li a:hover'

    def get_form_name(self):
        return "custom-css-account-hover-background-color"

    def get_title(self):
        return "Account name background color on hover"

    def get_default_color(self):
        return "#002664"


class HorizontalLineColorJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        return {'border-top': "2px solid {}".format(value.encode('utf-8'))}

    def get_class_name(self):
        return 'hr'

    def get_form_name(self):
        return "custom-css-horizontal-line"

    def get_title(self):
        return "Horizontal Line color"

    def get_default_color(self):
        return "#002664"


class CustomStyleProcessor:

    processors = [
        FooterBackGroundJob(),
        FooterColorJob(),

        NavigationHeaderBackGroundJob(),
        NavigationHeaderColorJob(),

        ModuleHeaderBackgroundColorJob(),
        ModuleHeaderColorJob(),

        AccountHoverBackgroundColorJob(),

        HorizontalLineColorJob(),


    ]

    def get_custom_css(self, data):
        result_css = defaultdict(dict)
        dump_css = {}
        for processor in self.processors:
            value = processor.get_css_from_data(data)
            if value is not None:
                result_css[processor.get_class_name()].update(value)
            dump_css[processor.get_form_name()] = {
                "value": value,
                "title": processor.get_title(),
                "default_value": processor.get_default_color()
            }

        result = "\n"
        for class_name, css in result_css.items():
            css = str(css).replace(',', ';').replace("'", "")
            result = "{previous_block}\n {class_name} {css}".format(
                previous_block=result,
                class_name=class_name,
                css=css)

        return result, dump_css


custom_style_processor = CustomStyleProcessor()
