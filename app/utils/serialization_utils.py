"""
Serialization utilities for handling non-JSON serializable objects.
"""

from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Union


def serialize_for_json(obj: Any) -> Any:
    """
    Convert non-JSON serializable objects to serializable format.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON serializable object
    """
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif hasattr(obj, 'dict'):  # Pydantic models
        return obj.dict()
    elif hasattr(obj, '__dict__'):  # Regular objects
        return {k: serialize_for_json(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, set):
        return [serialize_for_json(item) for item in obj]
    return obj


def safe_json_response(data: Any) -> Any:
    """
    Safely serialize data for JSON response.
    
    Args:
        data: Data to serialize
        
    Returns:
        JSON serializable data
    """
    if data is None:
        return None
    
    if isinstance(data, dict):
        return {k: serialize_for_json(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple, set)):
        return [serialize_for_json(item) for item in data]
    else:
        return serialize_for_json(data)


def convert_uuids_to_strings(data: Any) -> Any:
    """
    Convert all UUID objects in data to strings.
    
    Args:
        data: Data structure to process
        
    Returns:
        Data with UUIDs converted to strings
    """
    if isinstance(data, UUID):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_uuids_to_strings(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple, set)):
        return [convert_uuids_to_strings(item) for item in data]
    elif hasattr(data, '__dict__'):
        return {k: convert_uuids_to_strings(v) for k, v in data.__dict__.items() if not k.startswith('_')}
    return data
