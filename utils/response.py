"""
Response utilities for API serialization
"""
from pydantic import BaseModel
from typing import List, Any, Dict


def serialize_model(model: BaseModel, by_alias: bool = False) -> Dict[str, Any]:
    """
    Serialize a Pydantic model to dict with field names (not aliases)
    
    Args:
        model: Pydantic model instance
        by_alias: Whether to use field aliases (default: False for field names)
        
    Returns:
        Dict with serialized data
    """
    return model.model_dump(by_alias=by_alias, exclude_none=False)


def serialize_models(models: List[BaseModel], by_alias: bool = False) -> List[Dict[str, Any]]:
    """
    Serialize multiple Pydantic models to list of dicts
    
    Args:
        models: List of Pydantic model instances
        by_alias: Whether to use field aliases (default: False for field names)
        
    Returns:
        List of dicts with serialized data
    """
    return [model.model_dump(by_alias=by_alias, exclude_none=False) for model in models]
