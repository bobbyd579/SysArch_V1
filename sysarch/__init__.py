"""
Python Assembly System Library

A library for managing hierarchical assembly structures with parts, features, and connectors.
"""

__version__ = "1.0.0"

from .models import System, Assembly, Part, Feature, AssemblyItem, Connector
from .database import DatabaseManager
from .validators import (
    validate_circular_assembly,
    validate_connector,
    validate_assembly_item
)
from .queries import (
    list_parts_in_assembly,
    list_connections_for_part,
    list_connections_for_feature,
    get_assembly_hierarchy,
    list_all_features_for_part
)

__all__ = [
    'System',
    'Assembly',
    'Part',
    'Feature',
    'AssemblyItem',
    'Connector',
    'DatabaseManager',
    'validate_circular_assembly',
    'validate_connector',
    'validate_assembly_item',
    'list_parts_in_assembly',
    'list_connections_for_part',
    'list_connections_for_feature',
    'get_assembly_hierarchy',
    'list_all_features_for_part',
]

# GUI can be imported separately
try:
    from .gui import AssemblySystemGUI
    __all__.append('AssemblySystemGUI')
except ImportError:
    pass


