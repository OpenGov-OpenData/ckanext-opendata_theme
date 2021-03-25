# encoding: utf-8
from collections import OrderedDict

from ckan.plugins.toolkit import render, request

from ckanext.opendata_theme.opengov_custom_homepage.constants import LAYOUTS
from ckanext.opendata_theme.opengov_custom_homepage.processor import custom_naming_processor
from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.opendata_theme.opengov_custom_homepage.constants import CUSTOM_NAMING, CUSTOM_STYLE


class CustomCSSController(BaseCompatibilityController):
    redirect_to_action_kwargs = dict(endpoint='custom-homepage.custom_home_page')

    def custom_home_page(self):
        if request.method == 'POST':
            data = self.get_form_data(request)
            self.store_config(data)
        # Get last or default custom naming
        custom_naming = self.get_data(CUSTOM_NAMING)
        if not custom_naming:
            custom_naming = custom_naming_processor.get_custom_naming({})
            self.store_data(config_key=CUSTOM_NAMING, data=custom_naming)
        custom_naming = self.sort_inputs_by_title(custom_naming)

        # Get last or default layout
        actual_layout = self.get_data(CUSTOM_STYLE)
        if not actual_layout:
            actual_layout = 1
        return render(
            'admin/custom_home_page.html',
            extra_vars={
                "home_page_layouts_list": LAYOUTS,
                "custom_naming": custom_naming,
                "actual_layout": actual_layout
            }
        )

    def reset_custom_naming(self):
        extra_vars = {}
        naming = custom_naming_processor.get_custom_naming({})
        naming = self.sort_inputs_by_title(naming)
        self.store_data(CUSTOM_NAMING, naming)
        extra_vars["custom_naming"] = naming
        return self.redirect_to()

    def store_config(self, data):
        extra_vars = {}
        # Check and update home page layout style
        layout_style = data.get('custom_homepage_layout')
        if layout_style:
            self.store_data(CUSTOM_STYLE, layout_style)
        extra_vars["actual_layout"] = layout_style

        # Parse and save naming
        naming = custom_naming_processor.get_custom_naming(data)
        extra_vars["custom_naming"] = naming
        self.store_data(CUSTOM_NAMING, naming)

        self.redirect_to(extra_vars=extra_vars)

    @staticmethod
    def sort_inputs_by_title(css_metadata):
        list_for_sort = [(key, value) for key, value in css_metadata.items()]
        list_for_sort = sorted(list_for_sort, key=lambda x: x[1].get('title', 0))
        return OrderedDict(list_for_sort)
