"""
SQLite database layer for the assembly system.
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path

from .models import System, Assembly, Part, Feature, AssemblyItem, Connector


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    # Valid connector types
    VALID_CONNECTOR_TYPES = ['coincident', 'concentric', 'tangent', 'fixed']
    
    def __init__(self, db_path: str = "assembly_system.db"):
        """Initialize database manager with path to SQLite database."""
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists and create schema if needed."""
        if not Path(self.db_path).exists():
            self.create_schema()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_schema(self):
        """Create database schema with all tables and constraints."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Systems table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS systems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    overall_assembly_id INTEGER,
                    FOREIGN KEY (overall_assembly_id) REFERENCES assemblies(id)
                )
            """)
            
            # Assemblies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assemblies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    file_location TEXT NOT NULL,
                    image TEXT,
                    system_id INTEGER,
                    parent_assembly_id INTEGER,
                    FOREIGN KEY (system_id) REFERENCES systems(id),
                    FOREIGN KEY (parent_assembly_id) REFERENCES assemblies(id)
                )
            """)
            
            # Parts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    file_location TEXT NOT NULL
                )
            """)
            
            # Features table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    part_id INTEGER NOT NULL,
                    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE
                )
            """)
            
            # Assembly items table (instances)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assembly_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assembly_id INTEGER NOT NULL,
                    part_id INTEGER,
                    sub_assembly_id INTEGER,
                    instance_name TEXT NOT NULL,
                    FOREIGN KEY (assembly_id) REFERENCES assemblies(id) ON DELETE CASCADE,
                    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE,
                    FOREIGN KEY (sub_assembly_id) REFERENCES assemblies(id) ON DELETE CASCADE,
                    CHECK ((part_id IS NOT NULL AND sub_assembly_id IS NULL) OR 
                           (part_id IS NULL AND sub_assembly_id IS NOT NULL))
                )
            """)
            
            # Connectors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('coincident', 'concentric', 'tangent', 'fixed')),
                    feature1_id INTEGER NOT NULL,
                    feature2_id INTEGER NOT NULL,
                    assembly_item1_id INTEGER NOT NULL,
                    assembly_item2_id INTEGER NOT NULL,
                    FOREIGN KEY (feature1_id) REFERENCES features(id) ON DELETE CASCADE,
                    FOREIGN KEY (feature2_id) REFERENCES features(id) ON DELETE CASCADE,
                    FOREIGN KEY (assembly_item1_id) REFERENCES assembly_items(id) ON DELETE CASCADE,
                    FOREIGN KEY (assembly_item2_id) REFERENCES assembly_items(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
    
    # System CRUD operations
    def create_system(self, system: System) -> int:
        """Create a new system and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO systems (name, overall_assembly_id) VALUES (?, ?)",
                (system.name, system.overall_assembly_id)
            )
            return cursor.lastrowid
    
    def get_system(self, system_id: int) -> Optional[System]:
        """Get a system by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, overall_assembly_id FROM systems WHERE id = ?", (system_id,))
            row = cursor.fetchone()
            if row:
                return System(id=row[0], name=row[1], overall_assembly_id=row[2])
            return None
    
    def update_system(self, system: System):
        """Update an existing system."""
        if system.id is None:
            raise ValueError("System ID is required for update")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE systems SET name = ?, overall_assembly_id = ? WHERE id = ?",
                (system.name, system.overall_assembly_id, system.id)
            )
    
    def delete_system(self, system_id: int):
        """Delete a system."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM systems WHERE id = ?", (system_id,))
    
    # Assembly CRUD operations
    def create_assembly(self, assembly: Assembly) -> int:
        """Create a new assembly and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO assemblies (name, file_location, image, system_id, parent_assembly_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (assembly.name, assembly.file_location, assembly.image, 
                 assembly.system_id, assembly.parent_assembly_id)
            )
            return cursor.lastrowid
    
    def get_assembly(self, assembly_id: int) -> Optional[Assembly]:
        """Get an assembly by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, name, file_location, image, system_id, parent_assembly_id
                   FROM assemblies WHERE id = ?""",
                (assembly_id,)
            )
            row = cursor.fetchone()
            if row:
                return Assembly(
                    id=row[0], name=row[1], file_location=row[2], image=row[3],
                    system_id=row[4], parent_assembly_id=row[5]
                )
            return None
    
    def update_assembly(self, assembly: Assembly):
        """Update an existing assembly."""
        if assembly.id is None:
            raise ValueError("Assembly ID is required for update")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE assemblies SET name = ?, file_location = ?, image = ?,
                   system_id = ?, parent_assembly_id = ? WHERE id = ?""",
                (assembly.name, assembly.file_location, assembly.image,
                 assembly.system_id, assembly.parent_assembly_id, assembly.id)
            )
    
    def delete_assembly(self, assembly_id: int):
        """Delete an assembly."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assemblies WHERE id = ?", (assembly_id,))
    
    # Part CRUD operations
    def create_part(self, part: Part) -> int:
        """Create a new part and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO parts (name, file_location) VALUES (?, ?)",
                (part.name, part.file_location)
            )
            return cursor.lastrowid
    
    def get_part(self, part_id: int) -> Optional[Part]:
        """Get a part by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, file_location FROM parts WHERE id = ?", (part_id,))
            row = cursor.fetchone()
            if row:
                return Part(id=row[0], name=row[1], file_location=row[2])
            return None
    
    def update_part(self, part: Part):
        """Update an existing part."""
        if part.id is None:
            raise ValueError("Part ID is required for update")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE parts SET name = ?, file_location = ? WHERE id = ?",
                (part.name, part.file_location, part.id)
            )
    
    def delete_part(self, part_id: int):
        """Delete a part."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM parts WHERE id = ?", (part_id,))
    
    # Feature CRUD operations
    def create_feature(self, feature: Feature) -> int:
        """Create a new feature and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO features (name, part_id) VALUES (?, ?)",
                (feature.name, feature.part_id)
            )
            return cursor.lastrowid
    
    def get_feature(self, feature_id: int) -> Optional[Feature]:
        """Get a feature by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, part_id FROM features WHERE id = ?", (feature_id,))
            row = cursor.fetchone()
            if row:
                return Feature(id=row[0], name=row[1], part_id=row[2])
            return None
    
    def update_feature(self, feature: Feature):
        """Update an existing feature."""
        if feature.id is None:
            raise ValueError("Feature ID is required for update")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE features SET name = ?, part_id = ? WHERE id = ?",
                (feature.name, feature.part_id, feature.id)
            )
    
    def delete_feature(self, feature_id: int):
        """Delete a feature."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM features WHERE id = ?", (feature_id,))
    
    def get_features_for_part(self, part_id: int) -> List[Feature]:
        """Get all features for a part."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, part_id FROM features WHERE part_id = ?", (part_id,))
            return [Feature(id=row[0], name=row[1], part_id=row[2]) for row in cursor.fetchall()]
    
    # AssemblyItem CRUD operations
    def create_assembly_item(self, item: AssemblyItem) -> int:
        """Create a new assembly item and return its ID."""
        if item.part_id is None and item.sub_assembly_id is None:
            raise ValueError("Either part_id or sub_assembly_id must be set")
        if item.part_id is not None and item.sub_assembly_id is not None:
            raise ValueError("Cannot set both part_id and sub_assembly_id")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO assembly_items (assembly_id, part_id, sub_assembly_id, instance_name)
                   VALUES (?, ?, ?, ?)""",
                (item.assembly_id, item.part_id, item.sub_assembly_id, item.instance_name)
            )
            return cursor.lastrowid
    
    def get_assembly_item(self, item_id: int) -> Optional[AssemblyItem]:
        """Get an assembly item by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, assembly_id, part_id, sub_assembly_id, instance_name
                   FROM assembly_items WHERE id = ?""",
                (item_id,)
            )
            row = cursor.fetchone()
            if row:
                return AssemblyItem(
                    id=row[0], assembly_id=row[1], part_id=row[2],
                    sub_assembly_id=row[3], instance_name=row[4]
                )
            return None
    
    def update_assembly_item(self, item: AssemblyItem):
        """Update an existing assembly item."""
        if item.id is None:
            raise ValueError("AssemblyItem ID is required for update")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE assembly_items SET assembly_id = ?, part_id = ?,
                   sub_assembly_id = ?, instance_name = ? WHERE id = ?""",
                (item.assembly_id, item.part_id, item.sub_assembly_id, item.instance_name, item.id)
            )
    
    def delete_assembly_item(self, item_id: int):
        """Delete an assembly item."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assembly_items WHERE id = ?", (item_id,))
    
    def get_assembly_items_for_assembly(self, assembly_id: int) -> List[AssemblyItem]:
        """Get all assembly items for an assembly."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, assembly_id, part_id, sub_assembly_id, instance_name
                   FROM assembly_items WHERE assembly_id = ?""",
                (assembly_id,)
            )
            return [AssemblyItem(
                id=row[0], assembly_id=row[1], part_id=row[2],
                sub_assembly_id=row[3], instance_name=row[4]
            ) for row in cursor.fetchall()]
    
    # Connector CRUD operations
    def create_connector(self, connector: Connector) -> int:
        """Create a new connector and return its ID."""
        if connector.type not in self.VALID_CONNECTOR_TYPES:
            raise ValueError(f"Invalid connector type. Must be one of: {self.VALID_CONNECTOR_TYPES}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO connectors (type, feature1_id, feature2_id, assembly_item1_id, assembly_item2_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (connector.type, connector.feature1_id, connector.feature2_id,
                 connector.assembly_item1_id, connector.assembly_item2_id)
            )
            return cursor.lastrowid
    
    def get_connector(self, connector_id: int) -> Optional[Connector]:
        """Get a connector by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, type, feature1_id, feature2_id, assembly_item1_id, assembly_item2_id
                   FROM connectors WHERE id = ?""",
                (connector_id,)
            )
            row = cursor.fetchone()
            if row:
                return Connector(
                    id=row[0], type=row[1], feature1_id=row[2], feature2_id=row[3],
                    assembly_item1_id=row[4], assembly_item2_id=row[5]
                )
            return None
    
    def update_connector(self, connector: Connector):
        """Update an existing connector."""
        if connector.id is None:
            raise ValueError("Connector ID is required for update")
        if connector.type not in self.VALID_CONNECTOR_TYPES:
            raise ValueError(f"Invalid connector type. Must be one of: {self.VALID_CONNECTOR_TYPES}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE connectors SET type = ?, feature1_id = ?, feature2_id = ?,
                   assembly_item1_id = ?, assembly_item2_id = ? WHERE id = ?""",
                (connector.type, connector.feature1_id, connector.feature2_id,
                 connector.assembly_item1_id, connector.assembly_item2_id, connector.id)
            )
    
    def delete_connector(self, connector_id: int):
        """Delete a connector."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM connectors WHERE id = ?", (connector_id,))
    
    def get_connectors_for_feature(self, feature_id: int) -> List[Connector]:
        """Get all connectors involving a feature."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, type, feature1_id, feature2_id, assembly_item1_id, assembly_item2_id
                   FROM connectors WHERE feature1_id = ? OR feature2_id = ?""",
                (feature_id, feature_id)
            )
            return [Connector(
                id=row[0], type=row[1], feature1_id=row[2], feature2_id=row[3],
                assembly_item1_id=row[4], assembly_item2_id=row[5]
            ) for row in cursor.fetchall()]
    
    def get_connectors_for_assembly_item(self, item_id: int) -> List[Connector]:
        """Get all connectors involving an assembly item."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, type, feature1_id, feature2_id, assembly_item1_id, assembly_item2_id
                   FROM connectors WHERE assembly_item1_id = ? OR assembly_item2_id = ?""",
                (item_id, item_id)
            )
            return [Connector(
                id=row[0], type=row[1], feature1_id=row[2], feature2_id=row[3],
                assembly_item1_id=row[4], assembly_item2_id=row[5]
            ) for row in cursor.fetchall()]


