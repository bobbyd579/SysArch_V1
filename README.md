# Python Assembly System Library

A Python library for managing hierarchical assembly structures with parts, features, and connectors, backed by SQLite persistence.

## Features

- **Hierarchical Assemblies**: Assemblies can contain parts or other assemblies
- **Parts with Features**: Parts have features that are shared across all instances
- **Instance Management**: Multiple instances of the same part or sub-assembly within an assembly
- **Connectors**: Link specific features on specific instances with various constraint types
- **Circular Reference Prevention**: Prevents assemblies from containing themselves
- **SQLite Persistence**: Local file-based database with foreign key constraints
- **CLI Interface**: Simple command-line tools for common operations

## Installation

### Prerequisites

- Python 3.8 or later
- No external dependencies required - uses only Python standard library

### Setup Virtual Environment (Recommended)

1. **Install Python** (if not already installed):
   - Download from: https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation

2. **Create virtual environment**:
   
   **Windows (Command Prompt):**
   ```bash
   setup_venv.bat
   ```
   
   **Windows (PowerShell):**
   ```powershell
   .\setup_venv.ps1
   ```
   
   **Manual (all platforms):**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   
   **Windows (Command Prompt):**
   ```bash
   activate_venv.bat
   ```
   
   **Windows (PowerShell):**
   ```powershell
   .\activate_venv.ps1
   ```
   
   **Manual (Windows):**
   ```bash
   venv\Scripts\activate
   ```
   
   **Manual (Linux/Mac):**
   ```bash
   source venv/bin/activate
   ```

   You should see `(venv)` in your command prompt when activated.

For detailed setup instructions, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md).

## Quick Start

### Initialize Database

```bash
python manage_assembly.py init-db
```

### Launch GUI Application

```bash
python run_gui.py
```

The GUI provides a visual interface to:
- View parts and assemblies in a tree structure
- Create and delete parts
- View part and assembly attributes
- Manage features for parts
- Add part instances and sub-assemblies to assemblies

### Create a Part

```bash
python manage_assembly.py add-part --name "Bolt" --file-location "/path/to/bolt.step"
```

### Add Features to a Part

```bash
python manage_assembly.py add-feature --part-id 1 --name "Center Axis"
python manage_assembly.py add-feature --part-id 1 --name "Top Face"
```

### Create an Assembly

```bash
python manage_assembly.py add-assembly --name "Main Assembly" --file-location "/path/to/assembly.step"
```

### Add Part Instances to Assembly

```bash
python manage_assembly.py add-assembly-item --assembly-id 1 --part-id 1 --instance-name "Bolt-1"
python manage_assembly.py add-assembly-item --assembly-id 1 --part-id 1 --instance-name "Bolt-2"
```

### Create Connectors

```bash
python manage_assembly.py create-connector \
    --type coincident \
    --feature1-id 1 \
    --feature2-id 2 \
    --item1-id 1 \
    --item2-id 2
```

### Query Operations

```bash
# List all parts in an assembly
python manage_assembly.py list-parts --assembly-id 1

# List connections for a part
python manage_assembly.py list-connections --part-id 1

# Show assembly hierarchy
python manage_assembly.py show-assembly --assembly-id 1
```

## Library Usage

### Basic Example

```python
from sysarch import DatabaseManager, Part, Feature, Assembly, AssemblyItem, Connector

# Initialize database
db = DatabaseManager("my_assembly.db")
db.create_schema()

# Create a part
part = Part(name="Bolt", file_location="/path/to/bolt.step")
part_id = db.create_part(part)

# Add features to the part
feature1 = Feature(name="Center Axis", part_id=part_id)
feature1_id = db.create_feature(feature1)

feature2 = Feature(name="Top Face", part_id=part_id)
feature2_id = db.create_feature(feature2)

# Create an assembly
assembly = Assembly(name="Main Assembly", file_location="/path/to/assembly.step")
assembly_id = db.create_assembly(assembly)

# Add part instances
item1 = AssemblyItem(assembly_id=assembly_id, part_id=part_id, instance_name="Bolt-1")
item1_id = db.create_assembly_item(item1)

item2 = AssemblyItem(assembly_id=assembly_id, part_id=part_id, instance_name="Bolt-2")
item2_id = db.create_assembly_item(item2)

# Create a connector
connector = Connector(
    type="coincident",
    feature1_id=feature1_id,
    feature2_id=feature2_id,
    assembly_item1_id=item1_id,
    assembly_item2_id=item2_id
)
connector_id = db.create_connector(connector)
```

### Query Examples

```python
from sysarch import DatabaseManager
from sysarch.queries import list_parts_in_assembly, get_assembly_hierarchy

db = DatabaseManager("my_assembly.db")

# List all parts in an assembly (recursive)
parts = list_parts_in_assembly(db, assembly_id=1, recursive=True)
for part in parts:
    print(f"Part: {part['part_name']}, Instance: {part['instance_name']}")

# Get full assembly hierarchy
hierarchy = get_assembly_hierarchy(db, assembly_id=1)
print(hierarchy)
```

## Data Model

### System
- Container for one overall assembly
- Fields: `id`, `name`, `overall_assembly_id`

### Assembly
- Can contain parts or sub-assemblies
- Fields: `id`, `name`, `file_location`, `image`, `system_id`, `parent_assembly_id`
- Cannot contain itself (circular reference prevention)

### Part
- Individual items with features
- Fields: `id`, `name`, `file_location`
- Features are shared across all instances

### Feature
- Attributes of parts
- Fields: `id`, `name`, `part_id`
- All instances of a part share the same features

### AssemblyItem
- Instance of a part or sub-assembly within an assembly
- Fields: `id`, `assembly_id`, `part_id`, `sub_assembly_id`, `instance_name`
- Represents multiple instances of the same part/sub-assembly

### Connector
- Links two features on specific instances
- Fields: `id`, `type`, `feature1_id`, `feature2_id`, `assembly_item1_id`, `assembly_item2_id`
- Types: `coincident`, `concentric`, `tangent`, `fixed`
- Connects specific features on specific instances

## Database Schema

The library uses SQLite with the following tables:

- `systems`: System definitions
- `assemblies`: Assembly definitions
- `parts`: Part definitions
- `features`: Feature definitions (linked to parts)
- `assembly_items`: Instances of parts or sub-assemblies
- `connectors`: Links between features on instances

All tables have proper foreign key constraints and referential integrity.

## Validation

The library includes validation for:

- **Circular References**: Prevents assemblies from containing themselves
- **Connector Validation**: Ensures features belong to correct parts/instances
- **Assembly Item Validation**: Ensures either part_id or sub_assembly_id is set (not both)

## CLI Commands

- `init-db`: Initialize database schema
- `add-part`: Add a new part
- `add-feature`: Add a feature to a part
- `add-assembly`: Add a new assembly
- `add-assembly-item`: Add an assembly item (instance)
- `create-connector`: Create a connector between two features
- `list-parts`: List parts in an assembly
- `list-connections`: List connections for a part or feature
- `show-assembly`: Show assembly hierarchy

Use `python manage_assembly.py <command> --help` for detailed usage of each command.

## GUI Application

The GUI application provides a user-friendly interface for managing your assembly system:

### Features:
- **Tree View**: Browse parts and assemblies in a collapsible tree structure
- **Create Parts**: Add new parts with name and file location
- **Create Assemblies**: Add new assemblies with all attributes
- **View Attributes**: See all details for selected parts or assemblies
- **Manage Features**: Add and delete features for parts
- **Manage Children**: Add part instances or sub-assemblies to assemblies
- **Delete Items**: Remove parts, assemblies, features, or children

### Launch:
```bash
python run_gui.py
```

Or specify a custom database:
```bash
python run_gui.py my_custom_database.db
```

## License

This project is provided as-is for use in your projects.

