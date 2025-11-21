"""
Core data models for the assembly system.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class System:
    """Container for one overall assembly."""
    id: Optional[int] = None
    name: str = ""
    overall_assembly_id: Optional[int] = None


@dataclass
class Assembly:
    """Can contain parts or sub-assemblies."""
    id: Optional[int] = None
    name: str = ""
    file_location: str = ""
    image: Optional[str] = None
    system_id: Optional[int] = None
    parent_assembly_id: Optional[int] = None


@dataclass
class Part:
    """Individual items with features."""
    id: Optional[int] = None
    name: str = ""
    file_location: str = ""


@dataclass
class Feature:
    """Attributes of parts, shared across all instances."""
    id: Optional[int] = None
    name: str = ""
    part_id: int = 0


@dataclass
class AssemblyItem:
    """Instance of a part or sub-assembly within an assembly."""
    id: Optional[int] = None
    assembly_id: int = 0
    part_id: Optional[int] = None
    sub_assembly_id: Optional[int] = None
    instance_name: str = ""


@dataclass
class Connector:
    """Links two features on specific instances."""
    id: Optional[int] = None
    type: str = ""  # coincident, concentric, tangent, fixed, etc.
    feature1_id: int = 0
    feature2_id: int = 0
    assembly_item1_id: int = 0
    assembly_item2_id: int = 0


