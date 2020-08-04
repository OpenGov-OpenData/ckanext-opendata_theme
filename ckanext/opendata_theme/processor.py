from abc import abstractmethod
from collections import defaultdict

__all__ = ["custom_style_processor"]

from ckanext.opendata_theme.color_conrast import get_contrast


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


class FooterTextColor(AbstractParser):

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.site-footer'

    def get_form_name(self):
        return 'custom-css-footer-color'

    def get_title(self):
        return "Footer Text Color"

    def get_default_color(self):
        return "#ffffff"


class FooterBackGround(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.site-footer'

    def get_form_name(self):
        return "custom-css-footer-background-color"

    def get_title(self):
        return "Footer Background Color"

    def get_default_color(self):
        return "#1f76d8"


class NavigationHeaderBackGround(AbstractParser):
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


class NavigationHeaderColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.masthead'

    def get_form_name(self):
        return "custom-css-header-background-color"

    def get_default_color(self):
        return "#002664"

    def get_title(self):
        return "Navigation Header Text color"


class ModuleHeaderColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return "custom-css-module-header-color"

    def get_default_color(self):
        return "#ffffff"

    def get_title(self):
        return "Side Menu header text color"


class ModuleHeaderBackgroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return "custom-css-module-header-background-color"

    def get_default_color(self):
        return "red"

    def get_title(self):
        return "Side Menu header background color"


class AccountHoverBackgroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.account-masthead .account ul li a:hover'

    def get_form_name(self):
        return "custom-css-account-hover-background-color"

    def get_title(self):
        return "Account name background color on hover"

    def get_default_color(self):
        return "#1f76d8"


class HorizontalLineColor(AbstractParser):

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
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


class PaginationLinkBackgroundAndBorderColor(BasicPaginationLink):

    def get_form_name(self):
        return "custom-css-pagination-link-background-color"

    def get_title(self):
        return "Pagination Link Background Color"

    def get_default_color(self):
        return "#1f76d8"

    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {
                "border-color": self.color.encode('utf-8'),
                "background": self.color.encode('utf-8')
            }


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
        return "Headers Text Color "

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
    def __init__(self):
        self.processor_footer_background = FooterBackGround()
        self.processor_footer_text_color = FooterTextColor()

        self.processor_navigation_header_background = NavigationHeaderBackGround()
        self.processor_navigation_header_color = NavigationHeaderColor()

        self.processor_module_header_background_color = ModuleHeaderBackgroundColor()
        self.processor_module_header_color = ModuleHeaderColor()

        self.processor_account_hover_background_color = AccountHoverBackgroundColor()
        self.processor_horizontal_line = HorizontalLineColor()

        self.processor_pagination_background_color = PaginationLinkBackgroundAndBorderColor()
        self.processor_pagination_text_color = PaginationLinkTextColor()

        self.processor_hover_navigation_header = HoverOverNavigationHeaderButtonBackGroundColor()

        self.processor_account_header_background_color = AccountHeaderBackGroundColor()
        self.processor_account_header_color = AccountHeaderColor()

        self.processor_account_hover_background = AccountHoverBackgroundColor()

        self.processor_headers = Headers()
        self.processor_links = Links()
        self.processor_hover_links = HoverLinks()

        self.processors = [
            self.processor_footer_background,
            self.processor_footer_text_color,

            self.processor_navigation_header_background,
            self.processor_navigation_header_color,

            self.processor_module_header_background_color,
            self.processor_module_header_color,

            self.processor_navigation_header_background,

            self.processor_account_hover_background_color,

            self.processor_horizontal_line,

            self.processor_pagination_background_color,
            self.processor_pagination_text_color,

            self.processor_hover_navigation_header,

            self.processor_account_header_background_color,
            self.processor_account_header_color,

            self.processor_account_hover_background,

            self.processor_headers,
            self.processor_links,
            self.processor_hover_links
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

    def check_contrast(self):

        errors = {}
        pairs = [
            (self.processor_footer_background, self.processor_footer_text_color),
            (self.processor_navigation_header_background, self.processor_navigation_header_color),
            (self.processor_account_header_background_color, self.processor_account_header_color),
            (self.processor_module_header_background_color, self.processor_module_header_color),
            (self.processor_pagination_background_color, self.processor_pagination_text_color)
        ]
        for pair in pairs:
            pr_1 = pair[0]
            pr_2 = pair[1]
            contrast_value = get_contrast(pr_1.color, pr_2.color)
            if contrast_value <= 7:
                key = "{} and {}".format(
                    pr_1.get_title(),
                    pr_2.get_title())
                errors[key] = ["Does not have enough contrast."]
        return errors


custom_style_processor = CustomStyleProcessor()
