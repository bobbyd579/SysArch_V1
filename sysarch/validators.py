"""
Validation logic for the assembly system.
"""

from typing import Set, Optional, Tuple
from .database import DatabaseManager
from .models import Assembly, Connector, AssemblyItem


def validate_circular_assembly(db: DatabaseManager, assembly_id: int, potential_parent_id: int) -> bool:
    """
    Validate that adding an assembly as a child won't create a circular reference.
    
    Returns True if valid (no circular reference), False otherwise.
    """
    if assembly_id == potential_parent_id:
        return False
    
    # Check if potential_parent is a descendant of assembly_id
    visited: Set[int] = set()
    to_check = [potential_parent_id]
    
    while to_check:
        current_id = to_check.pop()
        if current_id == assembly_id:
            return False  # Circular reference detected
        
        if current_id in visited:
            continue
        visited.add(current_id)
        
        # Get all sub-assemblies of current_id
        items = db.get_assembly_items_for_assembly(current_id)
        for item in items:
            if item.sub_assembly_id is not None:
                to_check.append(item.sub_assembly_id)
    
    return True


def validate_connector(
    db: DatabaseManager,
    connector: Connector
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a connector is properly formed.
    
    Returns (is_valid, error_message).
    """
    # Check that features exist
    feature1 = db.get_feature(connector.feature1_id)
    feature2 = db.get_feature(connector.feature2_id)
    
    if feature1 is None:
        return False, f"Feature1 (ID: {connector.feature1_id}) does not exist"
    if feature2 is None:
        return False, f"Feature2 (ID: {connector.feature2_id}) does not exist"
    
    # Check that assembly items exist
    item1 = db.get_assembly_item(connector.assembly_item1_id)
    item2 = db.get_assembly_item(connector.assembly_item2_id)
    
    if item1 is None:
        return False, f"AssemblyItem1 (ID: {connector.assembly_item1_id}) does not exist"
    if item2 is None:
        return False, f"AssemblyItem2 (ID: {connector.assembly_item2_id}) does not exist"
    
    # Check that features belong to the correct parts
    # Get the parts for the assembly items
    part1_id = None
    part2_id = None
    
    if item1.part_id is not None:
        part1_id = item1.part_id
    elif item1.sub_assembly_id is not None:
        # For sub-assemblies, we need to check if the feature belongs to any part in that assembly
        # This is more complex - for now, we'll allow it but could add more validation
        pass
    
    if item2.part_id is not None:
        part2_id = item2.part_id
    
    # Validate feature1 belongs to part1
    if part1_id is not None and feature1.part_id != part1_id:
        return False, f"Feature1 (ID: {connector.feature1_id}) does not belong to the part of AssemblyItem1"
    
    # Validate feature2 belongs to part2
    if part2_id is not None and feature2.part_id != part2_id:
        return False, f"Feature2 (ID: {connector.feature2_id}) does not belong to the part of AssemblyItem2"
    
    # Check connector type
    if connector.type not in db.VALID_CONNECTOR_TYPES:
        return False, f"Invalid connector type: {connector.type}. Must be one of: {db.VALID_CONNECTOR_TYPES}"
    
    return True, None


def validate_assembly_item(
    db: DatabaseManager,
    item: AssemblyItem
) -> Tuple[bool, Optional[str]]:
    """
    Validate that an assembly item is properly formed.
    
    Returns (is_valid, error_message).
    """
    # Check that either part_id or sub_assembly_id is set, but not both
    if item.part_id is None and item.sub_assembly_id is None:
        return False, "Either part_id or sub_assembly_id must be set"
    
    if item.part_id is not None and item.sub_assembly_id is not None:
        return False, "Cannot set both part_id and sub_assembly_id"
    
    # Check that assembly exists
    assembly = db.get_assembly(item.assembly_id)
    if assembly is None:
        return False, f"Assembly (ID: {item.assembly_id}) does not exist"
    
    # Check that part exists (if part_id is set)
    if item.part_id is not None:
        part = db.get_part(item.part_id)
        if part is None:
            return False, f"Part (ID: {item.part_id}) does not exist"
    
    # Check that sub-assembly exists and validate no circular reference (if sub_assembly_id is set)
    if item.sub_assembly_id is not None:
        sub_assembly = db.get_assembly(item.sub_assembly_id)
        if sub_assembly is None:
            return False, f"Sub-assembly (ID: {item.sub_assembly_id}) does not exist"
        
        # Check for circular reference
        if not validate_circular_assembly(db, item.assembly_id, item.sub_assembly_id):
            return False, f"Adding sub-assembly {item.sub_assembly_id} to assembly {item.assembly_id} would create a circular reference"
    
    return True, None

