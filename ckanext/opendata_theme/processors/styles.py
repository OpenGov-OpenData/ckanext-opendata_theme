from abc import abstractmethod, ABCMeta
from collections import defaultdict, OrderedDict

import wcag_contrast_ratio as contrast

__all__ = ['CustomStyleProcessor']

from ckanext.opendata_theme.color_contrast import get_contrast


class AbstractParser:
    __metaclass__ = ABCMeta
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
    def get_title(self):
        raise NotImplementedError

    @abstractmethod
    def get_default_color(self):
        raise NotImplementedError


class AccountHeaderBackGroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.account-masthead'

    def get_form_name(self):
        return 'custom-css-account-header-background-color'

    def get_title(self):
        return 'Account Header Background Color'

    def get_default_color(self):
        return '#044187'


class AccountHeaderTextColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return ('.account-masthead .account ul li a,'
                '.account-masthead .account ul li a:hover')

    def get_form_name(self):
        return 'custom-css-account-header-color'

    def get_title(self):
        return 'Account Header Text Color'

    def get_default_color(self):
        return '#ffffff'


class AccountHoverBackgroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.account-masthead .account ul li a:hover'

    def get_form_name(self):
        return 'custom-css-account-hover-background-color'

    def get_title(self):
        return 'Account Header Hover Background Color'

    def get_default_color(self):
        return '#1f76d8'


class NavigationHeaderBackGroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.masthead'

    def get_form_name(self):
        return 'custom-css-header-background-color'

    def get_title(self):
        return 'Navigation Header Background Color'

    def get_default_color(self):
        return '#1f76d8'


class NavigationHeaderTextColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return ('.navbar .nav>li>a,'
                '.masthead .nav>li>a,'
                '.masthead .nav>li>a:focus,'
                '.masthead .nav>li>a:hover,'
                '.masthead .nav>.active>a,'
                '.masthead .nav>.active>a:hover,'
                '.masthead .nav>.active>a:focus')

    def get_form_name(self):
        return 'custom-css-header-text-color'

    def get_title(self):
        return 'Navigation Header Text color'

    def get_default_color(self):
        return '#ffffff'


class NavigationButtonHoverBackgroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background-color': self.color.encode('utf-8')}

    def get_class_name(self):
        return ('.masthead .navigation .nav-pills li a:hover,'
                '.masthead .navigation .nav-pills li.active a')

    def get_form_name(self):
        return 'custom-css-account-hover-navigation-button-background-color'

    def get_title(self):
        return 'Navigation Button Hover Background Color'

    def get_default_color(self):
        return '#044187'


class ModuleHeaderBackgroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return 'custom-css-module-header-background-color'

    def get_title(self):
        return 'Side Menu Header Background Color'

    def get_default_color(self):
        return '#1f76d8'


class ModuleHeaderTextColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return '.module-heading'

    def get_form_name(self):
        return 'custom-css-module-header-color'

    def get_title(self):
        return 'Side Menu Header Text Color'

    def get_default_color(self):
        return '#ffffff'


class FooterBackGroundColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'background': self.color.encode('utf-8')}

    def get_class_name(self):
        return 'body, .site-footer'

    def get_form_name(self):
        return 'custom-css-footer-background-color'

    def get_title(self):
        return 'Footer Background Color'

    def get_default_color(self):
        return '#383b3d'


class FooterTextColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return ('.site-footer,'
                '.site-footer label,'
                '.site-footer small')

    def get_form_name(self):
        return 'custom-css-footer-color'

    def get_title(self):
        return 'Footer Text Color'

    def get_default_color(self):
        return '#ffffff'


class LinkColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return 'a'

    def get_form_name(self):
        return 'custom-css-link-color'

    def get_title(self):
        return 'Link Color'

    def get_default_color(self):
        return '#131517'


class LinkHoverColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return 'a:hover'

    def get_form_name(self):
        return 'custom-css-link-hover-color'

    def get_title(self):
        return 'Link Hover Color'

    def get_default_color(self):
        return '#165cab'


class FooterLinkColor(AbstractParser):
    def get_css_from_data(self, data):
        self.parse_form_data(data)
        if self.color:
            return {'color': self.color.encode('utf-8')}

    def get_class_name(self):
        return ('.site-footer a,'
                '.site-footer a:hover')

    def get_form_name(self):
        return 'custom-css-footer-link-color'

    def get_title(self):
        return 'Footer Link Color'

    def get_default_color(self):
        return '#ffffff'


class CustomStyleProcessor:
    def __init__(self):
        self.processor_account_header_background_color = AccountHeaderBackGroundColor()
        self.processor_account_header_text_color = AccountHeaderTextColor()

        self.processor_account_hover_background_color = AccountHoverBackgroundColor()

        self.processor_navigation_header_background_color = NavigationHeaderBackGroundColor()
        self.processor_navigation_header_text_color = NavigationHeaderTextColor()

        self.processor_navigation_hover_background_color = NavigationButtonHoverBackgroundColor()

        self.processor_module_header_background_color = ModuleHeaderBackgroundColor()
        self.processor_module_header_text_color = ModuleHeaderTextColor()

        self.processor_footer_background_color = FooterBackGroundColor()
        self.processor_footer_text_color = FooterTextColor()

        self.processor_link_color = LinkColor()
        self.processor_link_hover_color = LinkHoverColor()

        self.processor_footer_link_color = FooterLinkColor()

        self.processors = [
            self.processor_account_header_background_color,
            self.processor_account_header_text_color,

            self.processor_account_hover_background_color,

            self.processor_navigation_header_background_color,
            self.processor_navigation_header_text_color,

            self.processor_navigation_hover_background_color,

            self.processor_module_header_background_color,
            self.processor_module_header_text_color,

            self.processor_footer_background_color,
            self.processor_footer_text_color,

            self.processor_link_color,
            self.processor_link_hover_color,

            self.processor_footer_link_color
        ]
        self.add_position_to_processors()

    def add_position_to_processors(self):
        for i, processor in enumerate(self.processors):
            processor.position = i

    def get_custom_css(self, data):
        result_css = defaultdict(dict)
        css_metadata = OrderedDict()

        for processor in self.processors:
            css_declaration = processor.get_css_from_data(data)
            if css_declaration is not None:
                result_css[processor.get_class_name()].update(css_declaration)

            css_metadata[processor.get_form_name()] = {
                'title': processor.get_title(),
                'value': processor.color or processor.get_default_color(),
                'position': processor.position
            }

        raw_css = '\n'
        for class_name, css_declaration in result_css.items():
            css_declaration = str(css_declaration).replace(',', ';').replace("'", "")
            raw_css = '{previous_block}\n {css_selector} {css_declaration}'.format(
                previous_block=raw_css,
                css_selector=class_name,
                css_declaration=css_declaration)

        return raw_css, css_metadata

    def check_contrast(self):
        errors = {}
        color_pairs = [
            (self.processor_account_header_background_color, self.processor_account_header_text_color),
            (self.processor_navigation_header_background_color, self.processor_navigation_header_text_color),
            (self.processor_module_header_background_color, self.processor_module_header_text_color),
            (self.processor_footer_background_color, self.processor_footer_text_color),
            (self.processor_footer_background_color, self.processor_footer_link_color)
        ]
        for pair in color_pairs:
            pr_1 = pair[0]
            pr_2 = pair[1]
            if pr_1.color and pr_2.color:
                contrast_value = get_contrast(pr_1.color, pr_2.color)
                if not contrast.passes_AA(contrast_value):
                    key = '{} and {}'.format(
                        pr_1.get_title(),
                        pr_2.get_title())
                    errors[key] = ['Contrast ratio is not high enough.']
        return errors
