# ckanext/myextension/blueprint.py
from ckan import model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, request, abort, render_template, jsonify
from datetime import datetime
import re
import logging

log = logging.getLogger(__name__)

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

def _is_valid_date(date_str):
    """Check if a string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_date_column(column_name, fields):
    """Check if a column is a date/timestamp type."""
    for field in fields:
        if field.get('id') == column_name:
            field_type = field.get('type', '').lower()
            return field_type in ('timestamp', 'timestamptz', 'date')
    return False

def datastore_search_sql_date_range(resource_id, column_name, start_date, end_date,
                                    filters, limit, fields):
    """
    Perform a datastore_search_sql query for date range filtering.
    Returns the response dictionary similar to datastore_search.
    """
    datastore_search_sql = toolkit.get_action('datastore_search_sql')
    
    # Get field type to determine how to handle the date comparison
    # Get field definitions first
    datastore_search = toolkit.get_action('datastore_search')
    field_info_result = datastore_search({}, {
        'resource_id': resource_id,
        'limit': 0
    })
    field_list = field_info_result.get('fields', [])
    is_date_type = is_date_column(column_name, field_list)
    
    # Log field type detection for debugging
    field_info = next((f for f in field_list if f.get('id') == column_name), None)
    if field_info:
        log.debug('Date field "%s" type: %s, is_date_type: %s', column_name, field_info.get('type'), is_date_type)
    else:
        log.warning('Date field "%s" not found in field list', column_name)
    
    # Build WHERE clause for date range
    # Escape column name to prevent SQL injection
    safe_column = '"{}"'.format(column_name.replace('"', '""'))
    
    # Escape date values to prevent SQL injection
    safe_start_date = start_date.replace("'", "''")
    safe_end_date = end_date.replace("'", "''")
    
    # Handle date comparison based on field type
    if is_date_type:
        # Field is already a date/timestamp type
        # Compare timestamps: start_date at beginning of day, end_date at end of day
        where_clauses = [
            '{} >= \'{}\'::date::timestamp'.format(safe_column, safe_start_date),
            '{} < (\'{}\'::date + interval \'1 day\')::timestamp'.format(safe_column, safe_end_date)
        ]
    else:
        # Field is text/varchar, need to cast to date for comparison
        # Try to cast the text field to date (handles YYYY-MM-DD format)
        where_clauses = [
            '{} IS NOT NULL AND {}::date >= \'{}\'::date'.format(safe_column, safe_column, safe_start_date),
            '{}::date < (\'{}\'::date + interval \'1 day\')'.format(safe_column, safe_end_date)
        ]
    
    # Add filters as additional WHERE conditions
    filter_conditions = []
    for filter_key, filter_values in filters.items():
        if isinstance(filter_values, list):
            if len(filter_values) == 1:
                safe_filter_key = '"{}"'.format(filter_key.replace('"', '""'))
                safe_filter_value = str(filter_values[0]).replace("'", "''")
                filter_conditions.append(
                    '{} = \'{}\''.format(safe_filter_key, safe_filter_value)
                )
            else:
                safe_filter_key = '"{}"'.format(filter_key.replace('"', '""'))
                values = ", ".join(["'" + str(v).replace("'", "''") + "'" for v in filter_values])
                filter_conditions.append('{} IN ({})'.format(safe_filter_key, values))
        else:
            safe_filter_key = '"{}"'.format(filter_key.replace('"', '""'))
            safe_filter_value = str(filter_values).replace("'", "''")
            filter_conditions.append(
                '{} = \'{}\''.format(safe_filter_key, safe_filter_value)
            )
    
    if filter_conditions:
        where_clauses.extend(filter_conditions)
    
    where_clause = ' AND '.join(where_clauses)
    
    # Build ORDER BY clause - quote column name to handle spaces
    order_by = '"_id" asc'
    
    # Build SELECT clause - escape column names
    select_fields = ', '.join(['"{}"'.format(col.replace('"', '""')) for col in fields])
    
    # CKAN datastore uses resource_id as table identifier
    # Escape resource_id for SQL
    safe_resource_id = resource_id.replace('"', '""')
    
    # Build SQL query - CKAN datastore_search_sql uses resource_id directly
    sql = 'SELECT {select_fields} FROM "{safe_resource_id}" WHERE {where_clause} ORDER BY {order_by} LIMIT {limit}'.format(
        select_fields=select_fields,
        safe_resource_id=safe_resource_id,
        where_clause=where_clause,
        order_by=order_by,
        limit=limit
    )
    
    # Also get total count for filtered results
    count_sql = 'SELECT COUNT(*) as total FROM "{safe_resource_id}" WHERE {where_clause}'.format(
        safe_resource_id=safe_resource_id,
        where_clause=where_clause
    )
    
    # Log SQL query for debugging
    log.debug('Date range SQL query: %s', sql)
    
    try:
        # Execute main query
        response = datastore_search_sql(
            None, {
                'sql': sql
            }
        )
        
        # Execute count query
        count_response = datastore_search_sql(
            None, {
                'sql': count_sql
            }
        )
        
        # datastore_search_sql returns records as list of dicts with column names as keys
        records = response.get('records', [])
        
        # Get total from count query
        count_records = count_response.get('records', [])
        total = count_records[0].get('total', 0) if count_records else 0
        
        # Log results for debugging
        log.debug('Date range query returned %d records (total: %d)', len(records), total)
        
        # Get field definitions from datastore_search (more reliable than datastore_info)
        datastore_search = toolkit.get_action('datastore_search')
        field_info_result = datastore_search({}, {
            'resource_id': resource_id,
            'limit': 0
        })
        
        # Create a mapping of field names to field definitions
        field_map = {f['id']: f for f in field_info_result.get('fields', [])}
        
        # Build result fields list
        result_fields = []
        for field_name in fields:
            if field_name in field_map:
                result_fields.append(field_map[field_name])
            else:
                # Fallback if field not found
                result_fields.append({'id': field_name, 'type': 'text'})
        
        return {
            'records': records,
            'total': total,
            'fields': result_fields
        }
    except Exception as e:
        raise Exception('SQL query error: {}'.format(str(e)))

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
    date_field = "Date of Execution (Formatted)"
    date_start_key = date_field + "_start"
    date_end_key = date_field + "_end"
    start_date = None
    end_date = None
    
    for key, value in request.args.items():
        if value:
            # Handle date range fields separately
            if key == date_start_key:
                if _is_valid_date(value):
                    start_date = value
                    filters[date_start_key] = value
            elif key == date_end_key:
                if _is_valid_date(value):
                    end_date = value
                    filters[date_end_key] = value
            else:
                # Get all values for this parameter (in case of multiple selections)
                values = request.args.getlist(key)
                if len(values) == 1:
                    filters[key] = values[0]
                elif len(values) > 1:
                    filters[key] = values

    # Get field list first (needed for both regular and date range queries)
    # Get configured filter fields from CKAN config
    filter_fields_config = toolkit.config.get('ckanext.custom_search.filter_fields', '')
    
    # Get all fields from datastore to determine which fields to use
    initial_data = {
        "resource_id": resource_id,
        "limit": 0
    }
    initial_result = toolkit.get_action("datastore_search")(context, initial_data)
    
    if filter_fields_config:
        # Parse comma or semicolon-separated field names from config
        # Support both separators for flexibility
        if ';' in filter_fields_config:
            configured_fields = [field.strip() for field in filter_fields_config.split(';') if field.strip()]
        else:
            configured_fields = [field.strip() for field in filter_fields_config.split(',') if field.strip()]
        # Only include fields that are both configured and exist in the dataset
        all_fields = [f["id"] for f in initial_result["fields"] if f["id"] != "_id"]
        fields = [field for field in configured_fields if field in all_fields]
    else:
        # Fallback to all fields if no configuration is provided
        fields = [f["id"] for f in initial_result["fields"] if f["id"] != "_id"]
    
    # Check if we have a date range filter
    # Verify the date field exists in the dataset
    all_field_names = [f["id"] for f in initial_result["fields"] if f["id"] != "_id"]
    date_field_exists = date_field in all_field_names
    
    if start_date and end_date and date_field_exists:
        # Use SQL query for date range filtering
        # Remove date range keys from filters for the SQL query (they're handled separately)
        sql_filters = {k: v for k, v in filters.items() if k not in [date_start_key, date_end_key]}
        
        try:
            result = datastore_search_sql_date_range(
                resource_id=resource_id,
                column_name=date_field,
                start_date=start_date,
                end_date=end_date,
                filters=sql_filters,
                limit=50,
                fields=all_field_names
            )
        except Exception as e:
            # Log the error for debugging
            log.error('Date range SQL query failed: %s', str(e))
            # Fall back to regular search if SQL query fails
            # Note: regular search won't support date ranges, so results may be empty
            data = {
                "resource_id": resource_id,
                "filters": sql_filters,  # Use sql_filters (without date range keys)
                "limit": 50
            }
            result = toolkit.get_action("datastore_search")(context, data)
    elif (start_date or end_date) and not date_field_exists:
        # Date field doesn't exist, use regular search without date filter
        log.warning('Date field "%s" not found in dataset, ignoring date range filter', date_field)
        data = {
            "resource_id": resource_id,
            "filters": {k: v for k, v in filters.items() if k not in [date_start_key, date_end_key]},
            "limit": 50
        }
        result = toolkit.get_action("datastore_search")(context, data)
    else:
        # Use regular datastore_search
        # Remove partial date range filters (only one date present) from filters
        # Date range requires both start and end dates
        filters_for_search = {k: v for k, v in filters.items() if k not in [date_start_key, date_end_key]}
        data = {
            "resource_id": resource_id,
            "filters": filters_for_search,
            "limit": 50
        }
        result = toolkit.get_action("datastore_search")(context, data)

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
    date_field = "Date of Execution (Formatted)"
    date_start_key = date_field + "_start"
    date_end_key = date_field + "_end"
    start_date = None
    end_date = None
    
    for key, value in request.args.items():
        if value and key != 'field':  # Don't include the field parameter itself
            # Handle date range fields separately
            if key == date_start_key:
                if _is_valid_date(value):
                    start_date = value
                    current_filters[date_start_key] = value
            elif key == date_end_key:
                if _is_valid_date(value):
                    end_date = value
                    current_filters[date_end_key] = value
            else:
                # Get all values for this parameter (in case of multiple selections)
                values = request.args.getlist(key)
                if len(values) == 1:
                    current_filters[key] = values[0]
                elif len(values) > 1:
                    current_filters[key] = values
    
    try:
        # Check if we have a date range filter
        if start_date and end_date:
            # Use SQL query for date range filtering
            # Remove date range keys from filters for the SQL query
            sql_filters = {k: v for k, v in current_filters.items() if k not in [date_start_key, date_end_key]}
            
            # Get all field names for the SQL query
            initial_data = {
                "resource_id": resource_id,
                "limit": 0
            }
            initial_result = toolkit.get_action("datastore_search")(context, initial_data)
            all_field_names = [f["id"] for f in initial_result["fields"] if f["id"] != "_id"]
            
            # Use SQL query with date range
            result = datastore_search_sql_date_range(
                resource_id=resource_id,
                column_name=date_field,
                start_date=start_date,
                end_date=end_date,
                filters=sql_filters,
                limit=25000,
                fields=all_field_names
            )
        else:
            # Use regular datastore_search
            data = {
                "resource_id": resource_id,
                "fields": [field],
                "distinct": True,
                "sort": field,
                "limit": 25000,  # Get up to 25000 distinct values
                "include_total": False
            }
            
            # Apply current filters to the search
            if current_filters:
                data["filters"] = current_filters
            
            result = toolkit.get_action("datastore_search")(context, data)
        
        # Extract distinct values for the requested field
        options = []
        seen = set()
        for record in result["records"]:
            if field in record and record[field] and record[field] not in seen:
                options.append(record[field])
                seen.add(record[field])
        
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