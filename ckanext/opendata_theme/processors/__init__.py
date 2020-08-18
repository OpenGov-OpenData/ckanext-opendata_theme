from ckanext.opendata_theme.processors.styles import CustomStyleProcessor
from ckanext.opendata_theme.processors.namings import CustomNamingProcessor

custom_style_processor = CustomStyleProcessor()
custom_naming_processor = CustomNamingProcessor()

__all__ = ["custom_style_processor", "custom_naming_processor"]
