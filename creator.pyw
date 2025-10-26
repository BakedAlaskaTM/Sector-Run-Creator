import tkinter as tk
from tkinter import *
from tkinter import simpledialog,messagebox
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog as fd
from pygbx import Gbx, GbxType
import re
import functions

# Variable Setup
config_dict = functions.read_config()
file_chosen = False

#window init
root = tk.Tk()
root.iconbitmap("SRC.ico")
root.title('Sector Run Creator')
root.resizable(True, True)
root.geometry('1280x720')
root.grid_columnconfigure(0,weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

text_scroll = Scrollbar()
text_left = scrolledtext.ScrolledText(root, font='Arial', background='black', foreground='white')
text_left.grid(column=0, row=2, sticky='NEWS')
text_right = scrolledtext.ScrolledText(root, font='Arial', background='black', foreground='white')
text_right.grid(column=1, row=2, sticky='NEWS')
if config_dict["DESTINATION"].strip() == "":
    intro = "Set a save destination to start..."
else:
    intro = "Open a replay..."
text_right.insert('1.0', intro)

def open_file():
    global file_chosen

    file_path = fd.askopenfilename(
        title='Open a Replay File',
        filetypes=[('Replay Files', '*.Gbx')]
    )
    inputs = functions.generate_sector_file(file_path, functions.read_config()["DESTINATION"])
    input_text = ""
    for block in inputs:
        for input in block:
            input_text += f"{input}\n"
        input_text += "\n"
    text_right.delete("1.0", END)
    text_right.insert("1.0", f"{input_text.strip()}\n")
    file_chosen = True
    return

open_button = ttk.Button(
    root,
    text='Open A Replay',
    command=open_file
)

def change_destination():
    file_path = fd.askdirectory(title='Select Destination Folder')
    config_dict = functions.read_config()
    config_file = open("config.txt", "w")
    for setting, value in config_dict.items():
        if setting == "DESTINATION":
            config_file.write(f"{setting}: {file_path}\n")
        else:
            config_file.write(f"{setting}: {value}\n")
    config_file.close()
    return

change_dir_button = ttk.Button(
    root,
    text='Change Save Location',
    command=change_destination
)

close_window_button = ttk.Button(
    root,
    text='Close Window',
    command=root.destroy
)

def check_save_directory():
    config_dict = functions.read_config()
    if config_dict["DESTINATION"].strip() == "":
        intro = "Set a save destination to start..."
        text_right.delete("1.0", END)
        text_right.insert("1.0", intro)
    elif not file_chosen:
        intro = "Open a replay..."
        text_right.delete("1.0", END)
        text_right.insert("1.0", intro)
    root.after(200, check_save_directory)

root.after(200, check_save_directory)

open_button.grid(column=0, row=0, sticky='NEWS', columnspan=2)
change_dir_button.grid(column=0, row=1, sticky='NEWS', columnspan=2)
close_window_button.grid(column=0, row=3, sticky='NEWS', columnspan=2)
root.mainloop()