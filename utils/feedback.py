# utils/feedback.py
import tkinter.messagebox as mbox

def vis_info(tittel, melding):
    mbox.showinfo(tittel, melding)

def vis_advarsel(tittel, melding):
    mbox.showwarning(tittel, melding)

def vis_feil(tittel, melding):
    mbox.showerror(tittel, melding)

def bekreftelse(tittel, melding):
    return mbox.askyesno(tittel, melding)