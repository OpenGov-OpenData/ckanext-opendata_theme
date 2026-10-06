RESOURCE_TYPE_CATEGORIES_KEY = 'ckanext.opendata_theme.resource_type_categories'
RESOURCE_TYPE_FILTER_ENABLED_KEY = 'ckanext.opendata_theme.resource_type_filter_enabled'

DEFAULT_RESOURCE_TYPE_CATEGORIES = {
    'tabular': {
        'label': 'Tabular Data',
        'enabled': True,
        'formats': ['CSV', 'XLS', 'XLSX', 'ODS', 'TSV', 'XLSM', 'csv', 'xls', 'xlsx', 'ods', 'tsv', 'xlsm'],
    },
    'documents': {
        'label': 'Documents',
        'enabled': True,
        'formats': ['PDF', 'DOC', 'DOCX', 'RTF', 'ODT', 'TXT', 'pdf', 'doc', 'docx', 'rtf', 'odt', 'txt'],
    },
    'images': {
        'label': 'Images',
        'enabled': False,
        'formats': [
            'PNG', 'JPG', 'JPEG', 'GIF', 'TIFF', 'SVG', 'BMP', 'WEBP', 'GeoTIFF',
            'png', 'jpg', 'jpeg', 'gif', 'tiff', 'svg', 'bmp', 'webp',
        ],
    },
    'maps': {
        'label': 'Maps',
        'enabled': True,
        'formats': [
            'GeoJSON', 'KML', 'KMZ', 'SHP', 'GML', 'WFS', 'WMS',
            'geojson', 'kml', 'kmz', 'shp', 'gml', 'wfs', 'wms',
            'Shapefile', 'shapefile', 'ESRI REST', 'esri rest',
        ],
    },
}
