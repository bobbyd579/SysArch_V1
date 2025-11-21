"""
Query methods for the assembly system.
"""

from typing import List, Dict, Any, Set
from .database import DatabaseManager
from .models import Part, Connector, Feature, AssemblyItem


def list_parts_in_assembly(db: DatabaseManager, assembly_id: int, recursive: bool = True) -> List[Dict[str, Any]]:
    """
    Get all parts in an assembly (direct and nested if recursive=True).
    
    Returns a list of dictionaries with part information and instance details.
    """
    parts: List[Dict[str, Any]] = []
    processed_assemblies: Set[int] = set()
    
    def _collect_parts(assembly_id: int, level: int = 0):
        if assembly_id in processed_assemblies:
            return
        processed_assemblies.add(assembly_id)
        
        items = db.get_assembly_items_for_assembly(assembly_id)
        for item in items:
            if item.part_id is not None:
                part = db.get_part(item.part_id)
                if part:
                    parts.append({
                        'part_id': part.id,
                        'part_name': part.name,
                        'part_file_location': part.file_location,
                        'instance_name': item.instance_name,
                        'assembly_id': assembly_id,
                        'level': level
                    })
            elif item.sub_assembly_id is not None and recursive:
                _collect_parts(item.sub_assembly_id, level + 1)
    
    _collect_parts(assembly_id)
    return parts


def list_connections_for_part(db: DatabaseManager, part_id: int) -> List[Dict[str, Any]]:
    """
    Show all connectors involving a part (across all instances).
    
    Returns a list of connector information.
    """
    connectors: List[Dict[str, Any]] = []
    
    # Get all features for this part
    features = db.get_features_for_part(part_id)
    feature_ids = {f.id for f in features}
    
    # Get all connectors involving these features
    all_connectors: Set[int] = set()
    for feature_id in feature_ids:
        conns = db.get_connectors_for_feature(feature_id)
        for conn in conns:
            if conn.id not in all_connectors:
                all_connectors.add(conn.id)
                connectors.append({
                    'connector_id': conn.id,
                    'type': conn.type,
                    'feature1_id': conn.feature1_id,
                    'feature2_id': conn.feature2_id,
                    'assembly_item1_id': conn.assembly_item1_id,
                    'assembly_item2_id': conn.assembly_item2_id
                })
    
    return connectors


def list_connections_for_feature(db: DatabaseManager, feature_id: int) -> List[Dict[str, Any]]:
    """
    Show all connectors for a specific feature.
    
    Returns a list of connector information.
    """
    connectors = db.get_connectors_for_feature(feature_id)
    return [
        {
            'connector_id': conn.id,
            'type': conn.type,
            'feature1_id': conn.feature1_id,
            'feature2_id': conn.feature2_id,
            'assembly_item1_id': conn.assembly_item1_id,
            'assembly_item2_id': conn.assembly_item2_id
        }
        for conn in connectors
    ]


def get_assembly_hierarchy(db: DatabaseManager, assembly_id: int) -> Dict[str, Any]:
    """
    Get full tree structure of an assembly.
    
    Returns a nested dictionary representing the hierarchy.
    """
    assembly = db.get_assembly(assembly_id)
    if assembly is None:
        return {}
    
    def _build_tree(assembly_id: int, visited: Set[int] = None) -> Dict[str, Any]:
        if visited is None:
            visited = set()
        
        if assembly_id in visited:
            return {'id': assembly_id, 'name': '... (circular reference prevented)', 'type': 'assembly'}
        
        visited.add(assembly_id)
        assembly = db.get_assembly(assembly_id)
        if assembly is None:
            return {}
        
        tree = {
            'id': assembly.id,
            'name': assembly.name,
            'file_location': assembly.file_location,
            'image': assembly.image,
            'type': 'assembly',
            'children': []
        }
        
        items = db.get_assembly_items_for_assembly(assembly_id)
        for item in items:
            if item.part_id is not None:
                part = db.get_part(item.part_id)
                if part:
                    tree['children'].append({
                        'id': item.id,
                        'name': item.instance_name,
                        'type': 'part_instance',
                        'part_id': part.id,
                        'part_name': part.name,
                        'part_file_location': part.file_location
                    })
            elif item.sub_assembly_id is not None:
                sub_tree = _build_tree(item.sub_assembly_id, visited.copy())
                sub_tree['instance_name'] = item.instance_name
                tree['children'].append(sub_tree)
        
        return tree
    
    return _build_tree(assembly_id)


def list_all_features_for_part(db: DatabaseManager, part_id: int) -> List[Feature]:
    """
    Get all features of a part.
    
    Returns a list of Feature objects.
    """
    return db.get_features_for_part(part_id)


def list_connections_for_assembly_item(db: DatabaseManager, item_id: int) -> List[Dict[str, Any]]:
    """
    Show all connectors involving a specific assembly item instance.
    
    Returns a list of connector information.
    """
    connectors = db.get_connectors_for_assembly_item(item_id)
    return [
        {
            'connector_id': conn.id,
            'type': conn.type,
            'feature1_id': conn.feature1_id,
            'feature2_id': conn.feature2_id,
            'assembly_item1_id': conn.assembly_item1_id,
            'assembly_item2_id': conn.assembly_item2_id
        }
        for conn in connectors
    ]


