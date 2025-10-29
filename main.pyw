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
sector_inputs = []
map_name = ""
inputs_saved = False

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
text_left.insert("1.0", "Summary:\n")

text_right = scrolledtext.ScrolledText(root, font='Arial', background='black', foreground='white')
text_right.grid(column=1, row=2, sticky='NEWS')
if config_dict["DESTINATION"].strip() == "":
    text_left.insert("2.0", "No save location set\n")
    intro_right = "Set a save location to start..."
else:
    text_left.insert("2.0", f"Save location: {config_dict['DESTINATION']}\n")
    intro_right = "Open a replay..."
text_right.insert('1.0', intro_right)

def open_file():
    global file_chosen
    global sector_inputs
    global map_name
    global inputs_saved
    file_path = fd.askopenfilename(
        title='Open a Replay File',
        filetypes=[('Replay Files', '*.Gbx')]
    )
    try:
        [map_name, author, num_cps, final_time, sector_inputs] = functions.generate_sector_inputs(file_path)
    except:
        return
    input_text = ""
    for block in sector_inputs:
        for input in block:
            input_text += f"{input}\n"
        input_text += "\n"
    text_left.delete("3.0", "9.0")
    text_left.insert("3.0", f"\nTrack Name: {map_name}\nAuthor: {author}\nCheckpoints: {num_cps}\nFinal Time: {final_time}\n")
    text_right.delete("1.0", END)
    text_right.insert("1.0", f"Inputs:\n{input_text.strip()}\n")
    file_chosen = True
    inputs_saved = False
    return

open_button = ttk.Button(
    root,
    text='Open A Replay',
    command=open_file
)

def change_destination():
    file_path = fd.askdirectory(title='Select Destination Folder')
    config_file = open("config.txt", "w")
    for setting, value in config_dict.items():
        if setting == "DESTINATION":
            config_file.write(f"{setting}: {file_path}\n")
        else:
            config_file.write(f"{setting}: {value}\n")
    config_file.close()
    text_left.delete("2.0", "3.0")
    text_left.insert("2.0", f"Save location: {file_path}\n")
    return

change_dir_button = ttk.Button(
    root,
    text='Change Save Location',
    command=change_destination
)

def save_inputs():
    global inputs_saved
    try:
        functions.create_file(config_dict["DESTINATION"], map_name, sector_inputs)
    except OSError as error:
        inputs_saved = False
        text_left.delete("7.0", "9.0")
        text_left.insert("7.0", f"\nInputs file did not save!\nReason: {error}")
    else:
        inputs_saved = True
        text_left.delete("7.0", "9.0")
        text_left.insert("7.0", f"\nInputs file saved successfully!\n")
    return

save_file_button = ttk.Button(
    root,
    text='Save Inputs',
    command=save_inputs
)

close_window_button = ttk.Button(
    root,
    text='Close Window',
    command=root.destroy
)

def check_save_directory():
    global config_dict
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
save_file_button.grid(column=0, row=3, sticky='NEWS', columnspan=2)
close_window_button.grid(column=0, row=4, sticky='NEWS', columnspan=2)
root.mainloop()