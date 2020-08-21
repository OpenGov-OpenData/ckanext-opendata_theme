from ckanext.opendata_theme.processors.styles import CustomStyleProcessor
from ckanext.opendata_theme.processors.namings import CustomNamingProcessor
from ckanext.opendata_theme.processors.footer import CustomFooterProcessor

custom_style_processor = CustomStyleProcessor()
custom_naming_processor = CustomNamingProcessor()
custom_footer_processor = CustomFooterProcessor()

__all__ = ["custom_style_processor", "custom_naming_processor", "custom_footer_processor"]
