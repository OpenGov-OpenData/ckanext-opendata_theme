# ckanext/myextension/blueprint.py
from ckan import model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, request, abort, render_template, jsonify
import re

search_blueprint = Blueprint("custom-search", __name__)

def get_iframe_url():
    """Get iframe_url from config or return None"""
    return toolkit.config.get('ckanext.custom_search.iframe_url') or None

def get_resource_id():
    """Extract RESOURCE_ID from iframe_url or return None"""
    iframe_url = get_iframe_url()
    
    if not iframe_url:
        return None
    
    # Extract resource_id from URL pattern: .../resource/{resource_id}/view/...
    # UUID pattern: 8-4-4-4-12 hexadecimal characters
    pattern = r'/resource/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(pattern, iframe_url, re.IGNORECASE)
    
    if match:
        return match.group(1)
    
    # Return None if extraction fails
    return None

def custom_search():
    context = {"model": model, "user": toolkit.g.user}
    
    resource_id = get_resource_id()
    base_iframe_url = get_iframe_url()
    
    # Check if configuration is missing
    if not base_iframe_url or not resource_id:
        return render_template(
            "custom_search/search.html",
            records=[],
            fields=[],
            filters={},
            iframe_url=None,
            config_missing=True
        )

    resource = toolkit.get_action('resource_show')(context, {'id': resource_id})
    package = toolkit.get_action('package_show')(context, {'id': resource.get('package_id')})

    if not package:
        abort(404, ('Package not found'))

    # Extract filters from query parameters (handle multiple values per filter)
    filters = {}
    for key, value in request.args.items():
        if value:
            # Get all values for this parameter (in case of multiple selections)
            values = request.args.getlist(key)
            if len(values) == 1:
                filters[key] = values[0]
            elif len(values) > 1:
                filters[key] = values

    # Build Datastore search params
    data = {
        "resource_id": resource_id,
        "filters": filters,
        "limit": 50
    }

    # Query Datastore
    result = toolkit.get_action("datastore_search")(context, data)

    # Get configured filter fields from CKAN config
    filter_fields_config = toolkit.config.get('ckanext.custom_search.filter_fields', '')
    
    if filter_fields_config:
        # Parse comma or semicolon-separated field names from config
        # Support both separators for flexibility
        if ';' in filter_fields_config:
            configured_fields = [field.strip() for field in filter_fields_config.split(';') if field.strip()]
        else:
            configured_fields = [field.strip() for field in filter_fields_config.split(',') if field.strip()]
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
        filters=filters,
        iframe_url=base_iframe_url,
        config_missing=False
    )

def get_filter_options():
    """API endpoint to get distinct values for a specific field, filtered by current filters"""
    context = {"model": model, "user": toolkit.g.user}
    
    field = request.args.get('field')
    if not field:
        return jsonify({"error": "Field parameter is required"}), 400
    
    resource_id = get_resource_id()
    
    if not resource_id:
        return jsonify({"error": "Custom search is not configured. Please configure the Resource View URL in the admin settings."}), 500
    
    # Extract current filters from query parameters (excluding the field we're getting options for)
    current_filters = {}
    for key, value in request.args.items():
        if value and key != 'field':  # Don't include the field parameter itself
            # Get all values for this parameter (in case of multiple selections)
            values = request.args.getlist(key)
            if len(values) == 1:
                current_filters[key] = values[0]
            elif len(values) > 1:
                current_filters[key] = values
    
    # Build Datastore search params for distinct values with current filters applied
    data = {
        "resource_id": resource_id,
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
    context = {"model": model, "user": toolkit.g.user}
    
    resource_id = get_resource_id()
    
    if not resource_id:
        return render_template("custom_search/browse.html", browse_items=[], browse_field=None, config_missing=True)

    # Discover the correct field name to browse for by checking the datastore schema
    candidate_browse_fields = [
        "Agency"
    ]

    try:
        info = toolkit.get_action("datastore_info")({}, {"id": resource_id})
        schema_fields = set(info.get("schema", {}).keys())
    except Exception:
        schema_fields = set()

    browse_field = None
    for name in candidate_browse_fields:
        if name in schema_fields:
            browse_field = name
            break

    # Fallback: if none of the candidates matched, try to infer by a simple heuristic
    if not browse_field and schema_fields:
        for name in schema_fields:
            lowered = name.lower()
            if "agency" in lowered:
                browse_field = name
                break

    browse_items = []
    if browse_field:
        # Get distinct list of browse items
        params = {
            "resource_id": resource_id,
            "fields": [browse_field],
            "distinct": True,
            "sort": browse_field,
            "limit": 1000,
            "include_total": False,
        }
        try:
            result = toolkit.get_action("datastore_search")(context, params)
            # Extract non-empty values
            browse_items = [rec[browse_field] for rec in result.get("records", []) if rec.get(browse_field)]
        except Exception:
            browse_items = []

    return render_template("custom_search/browse.html", browse_items=browse_items, browse_field=browse_field, config_missing=False)

search_blueprint.add_url_rule("/custom-search", methods=["GET", "POST"], view_func=custom_search)
search_blueprint.add_url_rule("/custom-browse", methods=["GET"], view_func=custom_browse)
search_blueprint.add_url_rule("/api/filter-options", methods=["GET"], view_func=get_filter_options)