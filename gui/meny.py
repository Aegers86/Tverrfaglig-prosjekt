# gui/meny.py

import tkinter as tk
from tkinter import messagebox

def lag_menylinje(root, main_window):
    menylinje = tk.Menu(root)
    root.config(menu=menylinje)

    filmeny = tk.Menu(menylinje, tearoff=0)
    filmeny.add_command(label="Startside", command=main_window.vis_startside)
    filmeny.add_separator()
    filmeny.add_command(label="Avslutt", command=main_window.avslutt)
    menylinje.add_cascade(label="Fil", menu=filmeny)

    vis_meny = tk.Menu(menylinje, tearoff=0)
    vis_meny.add_command(label="Kunder", command=main_window.navigasjon_map["Kunder"])
    vis_meny.add_command(label="Ordrer", command=main_window.navigasjon_map["Ordre"])
    vis_meny.add_command(label="Varelager", command=main_window.navigasjon_map["Varelager"])
    menylinje.add_cascade(label="Vis", menu=vis_meny)

    hjelpmeny = tk.Menu(menylinje, tearoff=0)
    hjelpmeny.add_command(label="Om", command=vis_om)
    menylinje.add_cascade(label="Hjelp", menu=hjelpmeny)

def vis_om():
    messagebox.showinfo("Om", "Tverrfaglig prosjekt - Varehus App\n\nLaget av Gruppe 1")
