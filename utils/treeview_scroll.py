# utils/treeview_scroll.py
import tkinter as tk

def legg_til_scrollbar(parent, tree):
    """Legger til vertikal og horisontal scrollbar på en Treeview."""
    # Vertikal scrollbar
    y_scroll = tk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=y_scroll.set)
    y_scroll.pack(side="right", fill="y")

    # Horisontal scrollbar
    x_scroll = tk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=x_scroll.set)
    x_scroll.pack(side="bottom", fill="x")

