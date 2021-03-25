# encoding: utf-8
import bleach

from ckan.logic import ValidationError

from ckan.plugins.toolkit import (
     render, request,
)

from ckanext.opendata_theme.opengov_custom_footer.constants import (
    CONFIG_SECTION, ALLOWED_HTML_TAGS, ALLOWED_ATTRIBUTES)

from ckanext.opendata_theme.base.compatibility_controller import BaseCompatibilityController


def clean_html(text):
    return bleach.clean(text, tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_ATTRIBUTES)


class CustomFooterCommonController(BaseCompatibilityController):
    default_data = {'layout_type': 1}
    redirect_to_action_kwargs = dict(endpoint='custom-footer.custom_footer')

    def custom_footer(self):
        custom_footer = self.get_custom_footer_metadata()
        if request.method == 'POST':
            data = self.get_form_data(request)
            custom_footer = {
                'layout_type': int(data.get('layout_type', 1)),
                'content_0': clean_html(data.get('content_0', '')),
                'content_1': clean_html(data.get('content_1', '')),
                'content_2': clean_html(data.get('content_2', '')),
                'content_3': clean_html(data.get('content_3', '')),
            }
            error = self.save_footer_metadata(custom_footer)
            custom_footer['errors'] = error

        return render('admin/custom_footer.html',
                      extra_vars=dict(data=custom_footer))

    def reset_custom_footer(self):
        self.save_footer_metadata({})
        return self.redirect_to({})

    @staticmethod
    def save_footer_metadata(custom_footer):
        try:
            CustomFooterCommonController.store_data(CONFIG_SECTION, custom_footer)
        except ValidationError as ex:
            return ex.error_summary

    @staticmethod
    def get_custom_footer_metadata():
        data = CustomFooterCommonController.get_data(CONFIG_SECTION)
        if not data:
            data = CustomFooterCommonController.default_data.copy()
        return data
