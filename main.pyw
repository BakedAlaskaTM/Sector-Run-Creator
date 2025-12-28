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
file_path = ""
sector_inputs = []
map_name = ""
ring_cps = []
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
text_right.grid(column=1, row=2, sticky='NEWS', rowspan=2)
if config_dict["DESTINATION"].strip() == "":
    text_left.insert("2.0", "No save location set\n")
    intro_right = "Set a save location to start..."
else:
    text_left.insert("2.0", f"Save location: {config_dict['DESTINATION']}\n")
    intro_right = "Open a replay..."
text_right.insert('1.0', intro_right)

def open_file():
    global file_chosen
    global file_path
    file_path = fd.askopenfilename(
        title='Open a Replay File',
        filetypes=[('Replay Files', '*.Gbx')]
    )
    process_file(True)
    file_chosen = True
    return

def process_file(from_open_file=False):
    global sector_inputs
    global map_name
    global inputs_saved
    global option_cache
    global ring_cps

    if not from_open_file:
        if option_cache == save_option.get():
            return
        option_cache = save_option.get()
        if file_path == "":
            return
    
    try:
        [map_name, author, num_cps, ring_cps, final_time, sector_inputs] = functions.generate_sector_inputs(file_path, option=save_option.get())
    except:
        messagebox.showerror("Error", "Failed to open replay file. Please ensure it is a valid .Gbx replay.")
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
    global file_path
    if file_path == "":
        tk.messagebox.showerror("Error", "No replay file opened.")
        return
    try:
        file_name = functions.create_file(config_dict["DESTINATION"], map_name, sector_inputs)
    except OSError as error:
        inputs_saved = False
        text_left.delete("7.0", "9.0")
        text_left.insert("7.0", f"\nInputs file did not save!\nReason: {error}")
    else:
        inputs_saved = True
        text_left.delete("7.0", "9.0")
        text_left.insert("7.0", f"\nSaved to {file_name}!\n")
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


labels = ring_cps  # 1–17
ring_cp_frame = Frame(root)
ring_cp_frame.grid(column=0, row=3, sticky='NEWS')

vars = []  # keep references to IntVars

num = 1
positions, rows, cols = functions.grid_positions(labels)

for label, r, c in positions:
    tk.Checkbutton(ring_cp_frame, text=str(label)).grid(
        row=r, column=c, padx=10, pady=5, sticky="w"
    )

for c in range(cols):
    ring_cp_frame.grid_columnconfigure(c, weight=1, uniform="x")

# Optional: make rows expand evenly too
for row in range(rows):
    ring_cp_frame.grid_rowconfigure(row, weight=1)

option_selector_frame = Frame(root)
option_selector_frame.grid(column=0, row=4, sticky='NEWS')

save_option = IntVar()
save_option.set(2)
option_cache = save_option.get()

values = {
    "No processing": 0,
    "Warps": 1,
    "No warps": 2
}

for (text, value) in values.items(): 
    Radiobutton(option_selector_frame, text = text, variable = save_option, command=process_file,
        value = value, indicator=0, background="light grey").pack(side=LEFT, expand=YES, fill=BOTH)

open_button.grid(column=0, row=0, sticky='NEWS', columnspan=2)
change_dir_button.grid(column=0, row=1, sticky='NEWS', columnspan=2)
save_file_button.grid(column=0, row=5, sticky='NEWS', columnspan=2)
close_window_button.grid(column=0, row=6, sticky='NEWS', columnspan=2)
root.mainloop()