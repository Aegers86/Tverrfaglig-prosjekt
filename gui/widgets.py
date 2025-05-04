# gui/widgets.py
# Gjenbrukbare komponenter som LabelEntry
import tkinter as tk
from tkinter import ttk

class LabelEntry(tk.Frame):
    def __init__(self, master, label_text):
        super().__init__(master)
        self.label = tk.Label(self, text=label_text)
        self.entry = tk.Entry(self)
        self.label.pack(side="left", padx=5)
        self.entry.pack(side="left", fill="x", expand=True)

    def get(self):
        return self.entry.get()

    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
class LabelText(tk.Frame):
    def __init__(self, master, label_text):
        super().__init__(master)
        self.label = tk.Label(self, text=label_text)
        self.text = tk.Text(self, wrap="word", height=4)
        self.label.pack(side="top", padx=5)
        self.text.pack(side="top", fill="x", expand=True)

    def get(self):
        return self.text.get("1.0", tk.END).strip()

    def set(self, text):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)

class LabelCombobox(tk.Frame):
    def __init__(self, master, label_text, values):
        super().__init__(master)
        self.label = tk.Label(self, text=label_text)
        self.combobox = ttk.Combobox(self, values=values)
        self.label.pack(side="left", padx=5)
        self.combobox.pack(side="left", fill="x", expand=True)

    def get(self):
        return self.combobox.get()

    def set(self, value):
        self.combobox.set(value)
    def set_values(self, values):
        self.combobox['values'] = values
        if values:
            self.combobox.current(0)
