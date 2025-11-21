#!/usr/bin/env python3
"""
CLI interface for managing assembly systems.
"""

import argparse
import sys
from pathlib import Path

from .database import DatabaseManager
from .models import System, Assembly, Part, Feature, AssemblyItem, Connector
from .validators import validate_connector, validate_assembly_item


def init_db_command(args):
    """Initialize the database schema."""
    db = DatabaseManager(args.db)
    db.create_schema()
    print(f"Database initialized at {args.db}")


def add_part_command(args):
    """Add a new part."""
    db = DatabaseManager(args.db)
    part = Part(name=args.name, file_location=args.file_location)
    part_id = db.create_part(part)
    print(f"Created part with ID: {part_id}")


def add_feature_command(args):
    """Add a feature to a part."""
    db = DatabaseManager(args.db)
    feature = Feature(name=args.name, part_id=args.part_id)
    feature_id = db.create_feature(feature)
    print(f"Created feature with ID: {feature_id}")


def add_assembly_command(args):
    """Add a new assembly."""
    db = DatabaseManager(args.db)
    assembly = Assembly(
        name=args.name,
        file_location=args.file_location,
        image=args.image,
        system_id=args.system_id,
        parent_assembly_id=args.parent_assembly_id
    )
    assembly_id = db.create_assembly(assembly)
    print(f"Created assembly with ID: {assembly_id}")


def add_assembly_item_command(args):
    """Add an assembly item (instance of part or sub-assembly)."""
    db = DatabaseManager(args.db)
    item = AssemblyItem(
        assembly_id=args.assembly_id,
        part_id=args.part_id,
        sub_assembly_id=args.sub_assembly_id,
        instance_name=args.instance_name
    )
    
    is_valid, error = validate_assembly_item(db, item)
    if not is_valid:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    
    item_id = db.create_assembly_item(item)
    print(f"Created assembly item with ID: {item_id}")


def create_connector_command(args):
    """Create a connector between two features."""
    db = DatabaseManager(args.db)
    connector = Connector(
        type=args.type,
        feature1_id=args.feature1_id,
        feature2_id=args.feature2_id,
        assembly_item1_id=args.item1_id,
        assembly_item2_id=args.item2_id
    )
    
    is_valid, error = validate_connector(db, connector)
    if not is_valid:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    
    connector_id = db.create_connector(connector)
    print(f"Created connector with ID: {connector_id}")


def list_parts_command(args):
    """List parts in an assembly."""
    db = DatabaseManager(args.db)
    from .queries import list_parts_in_assembly
    
    recursive = not getattr(args, 'no_recursive', False)
    parts = list_parts_in_assembly(db, args.assembly_id, recursive=recursive)
    
    if not parts:
        print("No parts found in assembly.")
        return
    
    print(f"\nParts in assembly {args.assembly_id}:")
    print("-" * 80)
    for part in parts:
        indent = "  " * part['level']
        print(f"{indent}Part ID: {part['part_id']}, Name: {part['part_name']}, "
              f"Instance: {part['instance_name']}, File: {part['part_file_location']}")


def list_connections_command(args):
    """List connections for a part or feature."""
    db = DatabaseManager(args.db)
    from .queries import list_connections_for_part, list_connections_for_feature
    
    if args.feature_id:
        connectors = list_connections_for_feature(db, args.feature_id)
        print(f"\nConnections for feature {args.feature_id}:")
    elif args.part_id:
        connectors = list_connections_for_part(db, args.part_id)
        print(f"\nConnections for part {args.part_id}:")
    else:
        print("Error: Either --part-id or --feature-id must be specified", file=sys.stderr)
        sys.exit(1)
    
    if not connectors:
        print("No connections found.")
        return
    
    print("-" * 80)
    for conn in connectors:
        print(f"Connector ID: {conn['connector_id']}, Type: {conn['type']}, "
              f"Feature1: {conn['feature1_id']}, Feature2: {conn['feature2_id']}, "
              f"Item1: {conn['assembly_item1_id']}, Item2: {conn['assembly_item2_id']}")


def show_assembly_command(args):
    """Show assembly hierarchy."""
    db = DatabaseManager(args.db)
    from .queries import get_assembly_hierarchy
    import json
    
    hierarchy = get_assembly_hierarchy(db, args.assembly_id)
    
    if not hierarchy:
        print(f"Assembly {args.assembly_id} not found.")
        return
    
    print(json.dumps(hierarchy, indent=2))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage assembly systems")
    parser.add_argument(
        '--db',
        default='assembly_system.db',
        help='Path to SQLite database file (default: assembly_system.db)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init-db
    init_parser = subparsers.add_parser('init-db', help='Initialize database schema')
    init_parser.set_defaults(func=init_db_command)
    
    # add-part
    add_part_parser = subparsers.add_parser('add-part', help='Add a new part')
    add_part_parser.add_argument('--name', required=True, help='Part name')
    add_part_parser.add_argument('--file-location', required=True, help='Part file location')
    add_part_parser.set_defaults(func=add_part_command)
    
    # add-feature
    add_feature_parser = subparsers.add_parser('add-feature', help='Add a feature to a part')
    add_feature_parser.add_argument('--part-id', type=int, required=True, help='Part ID')
    add_feature_parser.add_argument('--name', required=True, help='Feature name')
    add_feature_parser.set_defaults(func=add_feature_command)
    
    # add-assembly
    add_assembly_parser = subparsers.add_parser('add-assembly', help='Add a new assembly')
    add_assembly_parser.add_argument('--name', required=True, help='Assembly name')
    add_assembly_parser.add_argument('--file-location', required=True, help='Assembly file location')
    add_assembly_parser.add_argument('--image', help='Assembly image path')
    add_assembly_parser.add_argument('--system-id', type=int, help='System ID')
    add_assembly_parser.add_argument('--parent-assembly-id', type=int, help='Parent assembly ID')
    add_assembly_parser.set_defaults(func=add_assembly_command)
    
    # add-assembly-item
    add_item_parser = subparsers.add_parser('add-assembly-item', help='Add an assembly item (instance)')
    add_item_parser.add_argument('--assembly-id', type=int, required=True, help='Assembly ID')
    add_item_parser.add_argument('--part-id', type=int, help='Part ID (if adding a part instance)')
    add_item_parser.add_argument('--sub-assembly-id', type=int, help='Sub-assembly ID (if adding a sub-assembly instance)')
    add_item_parser.add_argument('--instance-name', required=True, help='Instance name')
    add_item_parser.set_defaults(func=add_assembly_item_command)
    
    # create-connector
    create_conn_parser = subparsers.add_parser('create-connector', help='Create a connector')
    create_conn_parser.add_argument('--type', required=True, 
                                   choices=['coincident', 'concentric', 'tangent', 'fixed'],
                                   help='Connector type')
    create_conn_parser.add_argument('--feature1-id', type=int, required=True, help='First feature ID')
    create_conn_parser.add_argument('--feature2-id', type=int, required=True, help='Second feature ID')
    create_conn_parser.add_argument('--item1-id', type=int, required=True, help='First assembly item ID')
    create_conn_parser.add_argument('--item2-id', type=int, required=True, help='Second assembly item ID')
    create_conn_parser.set_defaults(func=create_connector_command)
    
    # list-parts
    list_parts_parser = subparsers.add_parser('list-parts', help='List parts in an assembly')
    list_parts_parser.add_argument('--assembly-id', type=int, required=True, help='Assembly ID')
    list_parts_parser.add_argument('--no-recursive', action='store_true', 
                                   help='Only show direct parts (not nested)')
    list_parts_parser.set_defaults(func=list_parts_command)
    
    # list-connections
    list_conn_parser = subparsers.add_parser('list-connections', help='List connections')
    list_conn_parser.add_argument('--part-id', type=int, help='Part ID')
    list_conn_parser.add_argument('--feature-id', type=int, help='Feature ID')
    list_conn_parser.set_defaults(func=list_connections_command)
    
    # show-assembly
    show_assembly_parser = subparsers.add_parser('show-assembly', help='Show assembly hierarchy')
    show_assembly_parser.add_argument('--assembly-id', type=int, required=True, help='Assembly ID')
    show_assembly_parser.set_defaults(func=show_assembly_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()

