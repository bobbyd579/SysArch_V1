"""
GUI application for managing assembly systems.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any
from .database import DatabaseManager
from .models import Part, Assembly, Feature, AssemblyItem
from .queries import get_assembly_hierarchy, list_parts_in_assembly


class AssemblySystemGUI:
    """Main GUI application for assembly system management."""
    
    def __init__(self, root: tk.Tk, db_path: str = "assembly_system.db"):
        self.root = root
        self.root.title("Assembly System Manager")
        self.root.geometry("1200x800")
        
        self.db = DatabaseManager(db_path)
        self.db.create_schema()
        
        self.setup_ui()
        self.refresh_tree()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create main paned window for resizable panes
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane: Tree view
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Tree view frame with scrollbar
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tree view
        self.tree = ttk.Treeview(tree_frame, columns=("type", "id"), show="tree headings")
        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("id", text="ID")
        self.tree.column("#0", width=300)
        self.tree.column("type", width=150)
        self.tree.column("id", width=100)
        
        # Scrollbars for tree
        tree_vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_hscroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_vscroll.grid(row=0, column=1, sticky="ns")
        tree_hscroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_tree).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Add Part", command=self.add_part).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Add Assembly", command=self.add_assembly).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        
        # Right pane: Details view
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Details notebook (tabs)
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Attributes tab
        self.attributes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.attributes_frame, text="Attributes")
        
        # Attributes display with scrollbar
        attr_scroll = ttk.Scrollbar(self.attributes_frame)
        attr_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.attributes_text = tk.Text(self.attributes_frame, wrap=tk.WORD, yscrollcommand=attr_scroll.set)
        self.attributes_text.pack(fill=tk.BOTH, expand=True)
        attr_scroll.config(command=self.attributes_text.yview)
        
        # Features tab (for parts)
        self.features_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.features_frame, text="Features")
        
        # Features list with scrollbar
        features_scroll = ttk.Scrollbar(self.features_frame)
        features_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.features_listbox = tk.Listbox(self.features_frame, yscrollcommand=features_scroll.set)
        self.features_listbox.pack(fill=tk.BOTH, expand=True)
        features_scroll.config(command=self.features_listbox.yview)
        
        # Features buttons
        features_btn_frame = ttk.Frame(self.features_frame)
        features_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(features_btn_frame, text="Add Feature", command=self.add_feature).pack(side=tk.LEFT, padx=2)
        ttk.Button(features_btn_frame, text="Delete Feature", command=self.delete_feature).pack(side=tk.LEFT, padx=2)
        
        # Children tab (for assemblies)
        self.children_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.children_frame, text="Children")
        
        # Children list with scrollbar
        children_scroll = ttk.Scrollbar(self.children_frame)
        children_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.children_listbox = tk.Listbox(self.children_frame, yscrollcommand=children_scroll.set)
        self.children_listbox.pack(fill=tk.BOTH, expand=True)
        children_scroll.config(command=self.children_listbox.yview)
        
        # Children buttons
        children_btn_frame = ttk.Frame(self.children_frame)
        children_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(children_btn_frame, text="Add Part Instance", command=self.add_part_instance).pack(side=tk.LEFT, padx=2)
        ttk.Button(children_btn_frame, text="Add Sub-Assembly", command=self.add_sub_assembly).pack(side=tk.LEFT, padx=2)
        ttk.Button(children_btn_frame, text="Remove Child", command=self.remove_child).pack(side=tk.LEFT, padx=2)
        
        self.current_selection = None
        self.current_type = None
    
    def refresh_tree(self):
        """Refresh the tree view with current data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add parts
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, file_location FROM parts ORDER BY name")
            parts_root = self.tree.insert("", tk.END, text="Parts", values=("Category", ""), open=True)
            for row in cursor.fetchall():
                part_id, name, file_location = row
                self.tree.insert(parts_root, tk.END, text=name, 
                               values=("Part", part_id), tags=("part",))
        
        # Add assemblies
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, file_location FROM assemblies ORDER BY name")
            assemblies_root = self.tree.insert("", tk.END, text="Assemblies", 
                                             values=("Category", ""), open=True)
            for row in cursor.fetchall():
                assembly_id, name, file_location = row
                # Get children count
                items = self.db.get_assembly_items_for_assembly(assembly_id)
                child_count = len(items)
                display_name = f"{name} ({child_count} items)"
                self.tree.insert(assemblies_root, tk.END, text=display_name,
                               values=("Assembly", assembly_id), tags=("assembly",))
        
        # Configure tags
        self.tree.tag_configure("part", foreground="blue")
        self.tree.tag_configure("assembly", foreground="green")
    
    def on_tree_select(self, event):
        """Handle tree selection event."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        if not values or len(values) < 2:
            return
        
        item_type = values[0]
        item_id = values[1]
        
        if not item_id:
            self.current_selection = None
            self.current_type = None
            self.clear_details()
            return
        
        self.current_selection = int(item_id)
        self.current_type = item_type.lower()
        self.update_details()
    
    def on_tree_double_click(self, event):
        """Handle tree double-click event."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        if not values or len(values) < 2:
            return
        
        item_type = values[0]
        item_id = values[1]
        
        if item_type == "Assembly" and item_id:
            # Expand/collapse assembly children
            if self.tree.get_children(item):
                # Has children, toggle
                if self.tree.item(item, "open"):
                    self.tree.item(item, open=False)
                else:
                    self.tree.item(item, open=True)
            else:
                # Load children
                self.load_assembly_children(item, int(item_id))
    
    def load_assembly_children(self, parent_item, assembly_id):
        """Load children of an assembly into the tree."""
        items = self.db.get_assembly_items_for_assembly(assembly_id)
        for item in items:
            if item.part_id:
                part = self.db.get_part(item.part_id)
                if part:
                    self.tree.insert(parent_item, tk.END, text=f"{item.instance_name} ({part.name})",
                                   values=("Part Instance", item.id), tags=("part_instance",))
            elif item.sub_assembly_id:
                sub_assembly = self.db.get_assembly(item.sub_assembly_id)
                if sub_assembly:
                    self.tree.insert(parent_item, tk.END, text=f"{item.instance_name} ({sub_assembly.name})",
                                   values=("Sub-Assembly", item.sub_assembly_id), tags=("sub_assembly",))
    
    def update_details(self):
        """Update the details view based on current selection."""
        if not self.current_selection or not self.current_type:
            self.clear_details()
            return
        
        if self.current_type == "part":
            self.show_part_details(self.current_selection)
        elif self.current_type == "assembly":
            self.show_assembly_details(self.current_selection)
    
    def show_part_details(self, part_id: int):
        """Show details for a part."""
        part = self.db.get_part(part_id)
        if not part:
            return
        
        # Attributes
        self.attributes_text.delete(1.0, tk.END)
        self.attributes_text.insert(tk.END, f"Part Details\n")
        self.attributes_text.insert(tk.END, f"{'='*50}\n\n")
        self.attributes_text.insert(tk.END, f"ID: {part.id}\n")
        self.attributes_text.insert(tk.END, f"Name: {part.name}\n")
        self.attributes_text.insert(tk.END, f"File Location: {part.file_location}\n")
        
        # Features
        self.features_listbox.delete(0, tk.END)
        features = self.db.get_features_for_part(part_id)
        for feature in features:
            self.features_listbox.insert(tk.END, f"{feature.name} (ID: {feature.id})")
        
        # Hide children tab, show features tab
        self.notebook.hide(self.children_frame)
        self.notebook.add(self.features_frame, text="Features")
    
    def show_assembly_details(self, assembly_id: int):
        """Show details for an assembly."""
        assembly = self.db.get_assembly(assembly_id)
        if not assembly:
            return
        
        # Attributes
        self.attributes_text.delete(1.0, tk.END)
        self.attributes_text.insert(tk.END, f"Assembly Details\n")
        self.attributes_text.insert(tk.END, f"{'='*50}\n\n")
        self.attributes_text.insert(tk.END, f"ID: {assembly.id}\n")
        self.attributes_text.insert(tk.END, f"Name: {assembly.name}\n")
        self.attributes_text.insert(tk.END, f"File Location: {assembly.file_location}\n")
        if assembly.image:
            self.attributes_text.insert(tk.END, f"Image: {assembly.image}\n")
        if assembly.system_id:
            self.attributes_text.insert(tk.END, f"System ID: {assembly.system_id}\n")
        if assembly.parent_assembly_id:
            self.attributes_text.insert(tk.END, f"Parent Assembly ID: {assembly.parent_assembly_id}\n")
        
        # Children
        self.children_listbox.delete(0, tk.END)
        items = self.db.get_assembly_items_for_assembly(assembly_id)
        for item in items:
            if item.part_id:
                part = self.db.get_part(item.part_id)
                if part:
                    self.children_listbox.insert(tk.END, 
                        f"Part: {item.instance_name} ({part.name}) [ID: {item.id}]")
            elif item.sub_assembly_id:
                sub_assembly = self.db.get_assembly(item.sub_assembly_id)
                if sub_assembly:
                    self.children_listbox.insert(tk.END,
                        f"Sub-Assembly: {item.instance_name} ({sub_assembly.name}) [ID: {item.id}]")
        
        # Hide features tab, show children tab
        self.notebook.hide(self.features_frame)
        self.notebook.add(self.children_frame, text="Children")
    
    def clear_details(self):
        """Clear the details view."""
        self.attributes_text.delete(1.0, tk.END)
        self.features_listbox.delete(0, tk.END)
        self.children_listbox.delete(0, tk.END)
    
    def add_part(self):
        """Add a new part."""
        dialog = PartDialog(self.root, "Add Part")
        if dialog.result:
            part = Part(name=dialog.result["name"], file_location=dialog.result["file_location"])
            part_id = self.db.create_part(part)
            messagebox.showinfo("Success", f"Part created with ID: {part_id}")
            self.refresh_tree()
    
    def add_assembly(self):
        """Add a new assembly."""
        dialog = AssemblyDialog(self.root, "Add Assembly")
        if dialog.result:
            assembly = Assembly(
                name=dialog.result["name"],
                file_location=dialog.result["file_location"],
                image=dialog.result.get("image"),
                system_id=dialog.result.get("system_id"),
                parent_assembly_id=dialog.result.get("parent_assembly_id")
            )
            assembly_id = self.db.create_assembly(assembly)
            messagebox.showinfo("Success", f"Assembly created with ID: {assembly_id}")
            self.refresh_tree()
    
    def delete_selected(self):
        """Delete the selected item."""
        if not self.current_selection or not self.current_type:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        
        item_name = self.tree.item(self.tree.selection()[0], "text")
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            try:
                if self.current_type == "part":
                    self.db.delete_part(self.current_selection)
                elif self.current_type == "assembly":
                    self.db.delete_assembly(self.current_selection)
                messagebox.showinfo("Success", "Item deleted successfully.")
                self.current_selection = None
                self.current_type = None
                self.refresh_tree()
                self.clear_details()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    def add_feature(self):
        """Add a feature to the selected part."""
        if not self.current_selection or self.current_type != "part":
            messagebox.showwarning("No Part Selected", "Please select a part to add a feature to.")
            return
        
        name = simpledialog.askstring("Add Feature", "Enter feature name:")
        if name:
            feature = Feature(name=name, part_id=self.current_selection)
            feature_id = self.db.create_feature(feature)
            messagebox.showinfo("Success", f"Feature created with ID: {feature_id}")
            self.update_details()
    
    def delete_feature(self):
        """Delete selected feature."""
        selection = self.features_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a feature to delete.")
            return
        
        if not self.current_selection or self.current_type != "part":
            return
        
        feature_text = self.features_listbox.get(selection[0])
        # Extract ID from text like "Feature Name (ID: 123)"
        try:
            feature_id = int(feature_text.split("ID: ")[1].rstrip(")"))
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Could not parse feature ID.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete feature '{feature_text}'?"):
            self.db.delete_feature(feature_id)
            self.update_details()
    
    def add_part_instance(self):
        """Add a part instance to the selected assembly."""
        if not self.current_selection or self.current_type != "assembly":
            messagebox.showwarning("No Assembly Selected", "Please select an assembly.")
            return
        
        # Get list of parts
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM parts ORDER BY name")
            parts = cursor.fetchall()
        
        if not parts:
            messagebox.showwarning("No Parts", "No parts available. Please create a part first.")
            return
        
        dialog = PartInstanceDialog(self.root, "Add Part Instance", parts, self.current_selection)
        if dialog.result:
            item = AssemblyItem(
                assembly_id=self.current_selection,
                part_id=dialog.result["part_id"],
                instance_name=dialog.result["instance_name"]
            )
            from .validators import validate_assembly_item
            is_valid, error = validate_assembly_item(self.db, item)
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            item_id = self.db.create_assembly_item(item)
            messagebox.showinfo("Success", f"Part instance added with ID: {item_id}")
            self.update_details()
            self.refresh_tree()
    
    def add_sub_assembly(self):
        """Add a sub-assembly to the selected assembly."""
        if not self.current_selection or self.current_type != "assembly":
            messagebox.showwarning("No Assembly Selected", "Please select an assembly.")
            return
        
        # Get list of assemblies (excluding current)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM assemblies WHERE id != ? ORDER BY name", 
                         (self.current_selection,))
            assemblies = cursor.fetchall()
        
        if not assemblies:
            messagebox.showwarning("No Assemblies", "No other assemblies available.")
            return
        
        dialog = SubAssemblyDialog(self.root, "Add Sub-Assembly", assemblies, self.current_selection)
        if dialog.result:
            item = AssemblyItem(
                assembly_id=self.current_selection,
                sub_assembly_id=dialog.result["sub_assembly_id"],
                instance_name=dialog.result["instance_name"]
            )
            from .validators import validate_assembly_item
            is_valid, error = validate_assembly_item(self.db, item)
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            item_id = self.db.create_assembly_item(item)
            messagebox.showinfo("Success", f"Sub-assembly added with ID: {item_id}")
            self.update_details()
            self.refresh_tree()
    
    def remove_child(self):
        """Remove selected child from assembly."""
        selection = self.children_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a child to remove.")
            return
        
        if not self.current_selection or self.current_type != "assembly":
            return
        
        child_text = self.children_listbox.get(selection[0])
        # Extract ID from text like "Part: name (part_name) [ID: 123]"
        try:
            item_id = int(child_text.split("[ID: ")[1].rstrip("]"))
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Could not parse item ID.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Remove '{child_text}' from assembly?"):
            self.db.delete_assembly_item(item_id)
            self.update_details()
            self.refresh_tree()


class PartDialog:
    """Dialog for creating/editing a part."""
    
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("400x150")
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.dialog, text="File Location:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_entry = ttk.Entry(self.dialog, width=40)
        self.file_entry.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        self.name_entry.focus()
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_entry.get().strip()
        file_location = self.file_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Name is required.")
            return
        
        if not file_location:
            messagebox.showwarning("Validation", "File location is required.")
            return
        
        self.result = {"name": name, "file_location": file_location}
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


class AssemblyDialog:
    """Dialog for creating/editing an assembly."""
    
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("450x250")
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        row = 0
        ttk.Label(self.dialog, text="Name:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        ttk.Label(self.dialog, text="File Location:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_entry = ttk.Entry(self.dialog, width=40)
        self.file_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        ttk.Label(self.dialog, text="Image (optional):").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.image_entry = ttk.Entry(self.dialog, width=40)
        self.image_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        ttk.Label(self.dialog, text="System ID (optional):").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.system_id_entry = ttk.Entry(self.dialog, width=40)
        self.system_id_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        ttk.Label(self.dialog, text="Parent Assembly ID (optional):").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_id_entry = ttk.Entry(self.dialog, width=40)
        self.parent_id_entry.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        self.name_entry.focus()
        self.dialog.wait_window()
    
    def ok_clicked(self):
        name = self.name_entry.get().strip()
        file_location = self.file_entry.get().strip()
        image = self.image_entry.get().strip() or None
        system_id = self.system_id_entry.get().strip()
        parent_id = self.parent_id_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Name is required.")
            return
        
        if not file_location:
            messagebox.showwarning("Validation", "File location is required.")
            return
        
        result = {"name": name, "file_location": file_location}
        if image:
            result["image"] = image
        if system_id:
            try:
                result["system_id"] = int(system_id)
            except ValueError:
                messagebox.showwarning("Validation", "System ID must be a number.")
                return
        if parent_id:
            try:
                result["parent_assembly_id"] = int(parent_id)
            except ValueError:
                messagebox.showwarning("Validation", "Parent Assembly ID must be a number.")
                return
        
        self.result = result
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


class PartInstanceDialog:
    """Dialog for adding a part instance to an assembly."""
    
    def __init__(self, parent, title, parts, assembly_id):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("400x150")
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(self.dialog, text="Part:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.part_var = tk.StringVar()
        part_combo = ttk.Combobox(self.dialog, textvariable=self.part_var, width=37, state="readonly")
        part_combo['values'] = [f"{p[1]} (ID: {p[0]})" for p in parts]
        part_combo.grid(row=0, column=1, padx=5, pady=5)
        self.parts = parts
        
        ttk.Label(self.dialog, text="Instance Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.instance_entry = ttk.Entry(self.dialog, width=40)
        self.instance_entry.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        self.instance_entry.focus()
        self.dialog.wait_window()
    
    def ok_clicked(self):
        part_text = self.part_var.get()
        instance_name = self.instance_entry.get().strip()
        
        if not part_text:
            messagebox.showwarning("Validation", "Please select a part.")
            return
        
        if not instance_name:
            messagebox.showwarning("Validation", "Instance name is required.")
            return
        
        # Extract part ID
        try:
            part_id = int(part_text.split("ID: ")[1].rstrip(")"))
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Could not parse part ID.")
            return
        
        self.result = {"part_id": part_id, "instance_name": instance_name}
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


class SubAssemblyDialog:
    """Dialog for adding a sub-assembly to an assembly."""
    
    def __init__(self, parent, title, assemblies, parent_assembly_id):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("400x150")
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(self.dialog, text="Sub-Assembly:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.assembly_var = tk.StringVar()
        assembly_combo = ttk.Combobox(self.dialog, textvariable=self.assembly_var, width=37, state="readonly")
        assembly_combo['values'] = [f"{a[1]} (ID: {a[0]})" for a in assemblies]
        assembly_combo.grid(row=0, column=1, padx=5, pady=5)
        self.assemblies = assemblies
        
        ttk.Label(self.dialog, text="Instance Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.instance_entry = ttk.Entry(self.dialog, width=40)
        self.instance_entry.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        self.instance_entry.focus()
        self.dialog.wait_window()
    
    def ok_clicked(self):
        assembly_text = self.assembly_var.get()
        instance_name = self.instance_entry.get().strip()
        
        if not assembly_text:
            messagebox.showwarning("Validation", "Please select a sub-assembly.")
            return
        
        if not instance_name:
            messagebox.showwarning("Validation", "Instance name is required.")
            return
        
        # Extract assembly ID
        try:
            assembly_id = int(assembly_text.split("ID: ")[1].rstrip(")"))
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Could not parse assembly ID.")
            return
        
        self.result = {"sub_assembly_id": assembly_id, "instance_name": instance_name}
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


def main():
    """Main entry point for GUI application."""
    import sys
    
    root = tk.Tk()
    db_path = sys.argv[1] if len(sys.argv) > 1 else "assembly_system.db"
    app = AssemblySystemGUI(root, db_path)
    root.mainloop()


if __name__ == "__main__":
    main()

