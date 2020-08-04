from abc import ABCMeta, abstractmethod
from collections import defaultdict

__all__ = ["custom_style_processor"]


class AbstractParser:
    color = None

    @abstractmethod
    def get_css_from_data(self, data):
        return

    def parse_form_data(self, data):
        value = data.get(self.get_form_name())
        self.color = value

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


class FooterTextColorJob(AbstractParser):

    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        self.color = value
        return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.site-footer'

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
        self.color = value
        return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.site-footer'

    def get_form_name(self):
        return "custom-css-footer-background-color"

    def get_title(self):
        return "Footer Background Color"

    def get_default_color(self):
        return "#1f76d8"


class NavigationHeaderBackGroundJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        self.color = value
        return {'background': self.color.encode('utf-8')}

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
        self.color = value
        return {'color': self.color.encode('utf-8')}

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
        self.color = value
        return {'color': self.color.encode('utf-8')}

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
        self.color = value
        return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return "custom-css-module-header-background-color"

    def get_default_color(self):
        return "red"

    def get_title(self):
        return "Side Menu header background color"


class AccountHoverBackgroundColorJob(AbstractParser):
    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        self.color = value
        return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.account-masthead .account ul li a:hover'

    def get_form_name(self):
        return "custom-css-account-hover-background-color"

    def get_title(self):
        return "Account name background color on hover"

    def get_default_color(self):
        return "#1f76d8"


class HorizontalLineColorJob(AbstractParser):

    def get_css_from_data(self, data):
        value = data.get(self.get_form_name())
        if not value:
            return
        self.color = value
        return {'border-top': "2px solid {}".format(self.color.encode('utf-8'))}

    def get_class_name(self):
        return 'hr'

    def get_form_name(self):
        return "custom-css-horizontal-line"

    def get_title(self):
        return "Horizontal Line color"

    def get_default_color(self):
        return "#002664"


class BasicPaginationLink(AbstractParser):

    def get_class_name(self):
        return (".pagination li.active a,"
                ".pagination li.active span,"
                ".pagination li.active a:hover,"
                ".pagination li.active span:hover,"
                ".pagination li.active a:focus,"
                ".pagination li.active span:focus")


class PaginationLinkTextColor(BasicPaginationLink):

    def get_form_name(self):
        return "custom-css-pagination-link-color"

    def get_title(self):
        return "Pagination Link Text Color"

    def get_default_color(self):
        return "#ffffff"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"color": self.color.encode('utf-8')}


class PaginationLinkBackgroundColor(BasicPaginationLink):

    def get_form_name(self):
        return "custom-css-pagination-link-background-color"

    def get_title(self):
        return "Pagination Link Background Color"

    def get_default_color(self):
        return "#1f76d8"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"background": self.color.encode('utf-8')}


class PaginationLinkBorderColor(BasicPaginationLink):

    def get_form_name(self):
        return "custom-css-pagination-link-border-color"

    def get_title(self):
        return "Pagination Link Text Color"

    def get_default_color(self):
        return "#1f76d8"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"border-color": self.color.encode('utf-8')}


class AccountHeaderBackGroundColor(AbstractParser):

    def get_class_name(self):
        return ".account-masthead"

    def get_form_name(self):
        return "custom-css-account-header-background-color"

    def get_title(self):
        return "Account Header Background Color"

    def get_default_color(self):
        return "#044187"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"background": self.color.encode('utf-8')}


class AccountHeaderColor(AbstractParser):

    def get_class_name(self):
        return ".account-masthead"

    def get_form_name(self):
        return "custom-css-account-header-color"

    def get_title(self):
        return "Account Header Text Color"

    def get_default_color(self):
        return "#ffffff"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"color": self.color.encode('utf-8')}


class HoverOverNavigationHeaderButtonBackGroundColor(AbstractParser):

    def get_class_name(self):
        return (".masthead .navigation .nav-pills li a:hover,"
                ".masthead .navigation .nav-pills li.active a")

    def get_form_name(self):
        return "custom-css-account-hover-navigation-button-background-color"

    def get_title(self):
        return "Hover Over navigation button"

    def get_default_color(self):
        return "#044187"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"background-color": self.color.encode('utf-8')}


class Headers(AbstractParser):
    def get_class_name(self):
        return "h1, h2, h3, h4, h5, h6"

    def get_form_name(self):
        return "custom-css-headers"

    def get_title(self):
        return "Headers ??? "

    def get_default_color(self):
        return "#131517"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"color": self.color.encode('utf-8')}


class Links(AbstractParser):
    def get_class_name(self):
        return "a"

    def get_form_name(self):
        return "custom-css-links"

    def get_title(self):
        return "Links"

    def get_default_color(self):
        return "#165cab"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"color": self.color.encode('utf-8')}


class HoverLinks(AbstractParser):
    def get_class_name(self):
        return "a:hover"

    def get_form_name(self):
        return "custom-css-links-hover"

    def get_title(self):
        return "Hover Links"

    def get_default_color(self):
        return "#131517"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {"color": self.color.encode('utf-8')}


class CustomStyleProcessor:
    processors = [
        FooterBackGroundJob(),
        FooterTextColorJob(),

        NavigationHeaderBackGroundJob(),
        NavigationHeaderColorJob(),

        ModuleHeaderBackgroundColorJob(),
        ModuleHeaderColorJob(),

        AccountHoverBackgroundColorJob(),

        HorizontalLineColorJob(),


        PaginationLinkBackgroundColor(),
        PaginationLinkTextColor(),
        PaginationLinkBorderColor(),

        HoverOverNavigationHeaderButtonBackGroundColor(),

        AccountHeaderBackGroundColor(),
        AccountHeaderColor(),

        AccountHoverBackgroundColorJob(),

        Headers(),
        Links(),
        HoverLinks()

    ]

    def get_custom_css(self, data):
        result_css = defaultdict(dict)
        dump_css = {}
        for processor in self.processors:
            value = processor.get_css_from_data(data)
            if value is not None:
                result_css[processor.get_class_name()].update(value)
            dump_css[processor.get_form_name()] = {
                "value": processor.color or processor.get_default_color(),
                "title": processor.get_title()
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

