import tkinter as tk #Importerer tkinter
from tkinter import ttk #Importerer ttk fra tkinter

root = tk.Tk() #Lager et vindu
root.geometry("800x500") #Setter størrelsen på vinduet
root.title("Tverrfaglig prosjekt") #Setter tittelen på vinduet

#Lager en label
label = tk.Label(root, text="Velkommen til tverrfaglig prosjekt", font=("Arial", 18)) #Lager en label
label.pack(padx=10, pady=10) #Plasserer labelen i vinduet

#lage en tekstboks
textbox = tk.Text(root, height=10, width=50, font=("Arial", 14)) #Lager en tekstboks
textbox.pack(padx=10, pady=10) #Plasserer tekstboksen i vinduet

#Lager en knapp
button = tk.Button(root, text="Klikk her", font=("Arial", 14)) #Lager en knapp
button.pack(padx=10, pady=10) #Plasserer knappen i vinduet

root.mainloop() #Starter grensesnittet