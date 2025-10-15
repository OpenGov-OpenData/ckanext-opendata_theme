# ckanext/myextension/blueprint.py
from ckan import model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, request, abort, render_template, jsonify

search_blueprint = Blueprint("custom-search", __name__)

RESOURCE_ID = "cf86d944-0db9-4d4e-a666-bc9640be16fd"

def custom_search():
    context = {"model": model, "user": toolkit.g.user}

    resource = toolkit.get_action('resource_show')(context, {'id': RESOURCE_ID})
    package = toolkit.get_action('package_show')(context, {'id': resource.get('package_id')})

    if not package:
        abort(404, ('Package not found'))

    # Extract filters from query parameters
    filters = {}
    for key, value in request.args.items():
        if value:
            filters[key] = value

    # Build Datastore search params
    data = {
        "resource_id": RESOURCE_ID,
        "filters": filters,
        "limit": 50
    }

    # Query Datastore
    result = toolkit.get_action("datastore_search")(context, data)

    # Get configured filter fields from CKAN config
    filter_fields_config = toolkit.config.get('ckanext.custom_search.filter_fields', '')
    
    if filter_fields_config:
        # Parse comma-separated field names from config
        configured_fields = [field.strip() for field in filter_fields_config.split(';') if field.strip()]
        # Only include fields that are both configured and exist in the dataset
        all_fields = [f["id"] for f in result["fields"] if f["id"] != "_id"]
        fields = [field for field in configured_fields if field in all_fields]
    else:
        # Fallback to all fields if no configuration is provided
        fields = [f["id"] for f in result["fields"] if f["id"] != "_id"]

    return render_template(
        "custom_search/search.html",
        records=result["records"],
        fields=fields,
        filters=filters
    )

def get_filter_options():
    """API endpoint to get distinct values for a specific field, filtered by current filters"""
    context = {"model": model, "user": toolkit.g.user}
    
    field = request.args.get('field')
    if not field:
        return jsonify({"error": "Field parameter is required"}), 400
    
    # Extract current filters from query parameters (excluding the field we're getting options for)
    current_filters = {}
    for key, value in request.args.items():
        if value and key != 'field':  # Don't include the field parameter itself
            current_filters[key] = value
    
    # Build Datastore search params for distinct values with current filters applied
    data = {
        "resource_id": RESOURCE_ID,
        "fields": [field],
        "distinct": True,
        "sort": field,
        "limit": 1000,  # Get all distinct values
        "include_total": False
    }
    
    # Apply current filters to the search
    if current_filters:
        data["filters"] = current_filters
    
    try:
        result = toolkit.get_action("datastore_search")(context, data)
        options = []
        for record in result["records"]:
            if record[field]:  # Only include non-empty values
                options.append(record[field])
        
        return jsonify({"options": options})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def custom_browse():
    return render_template("custom_search/browse.html")

search_blueprint.add_url_rule("/custom-search", methods=["GET", "POST"], view_func=custom_search)
search_blueprint.add_url_rule("/custom-browse", methods=["GET"], view_func=custom_browse)
search_blueprint.add_url_rule("/api/filter-options", methods=["GET"], view_func=get_filter_options)