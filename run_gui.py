#!/usr/bin/env python3
"""
GUI launcher for the Assembly System Manager.
"""

import sys
import tkinter as tk
from sysarch.gui import AssemblySystemGUI

if __name__ == "__main__":
    root = tk.Tk()
    db_path = sys.argv[1] if len(sys.argv) > 1 else "assembly_system.db"
    app = AssemblySystemGUI(root, db_path)
    root.mainloop()

