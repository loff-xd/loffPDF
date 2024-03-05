import tkinter as tk
import tkinter.filedialog
from tkinter import messagebox
import ntpath

from backend import *

supported_filetypes = [
    ".pdf",
    ".jpg",
    ".png"
]


class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.file_list = []

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=0)

        self.bt_open = tk.Button(self, text="Open/Add", command=self.open_file)
        self.bt_open.grid(column=0, row=0)

        self.bt_remove = tk.Button(self, text="Remove", command=self.remove_item)
        self.bt_remove.grid(column=1, row=0)

        self.bt_remove = tk.Button(self, text="Clear", command=self.clear_all)
        self.bt_remove.grid(column=2, row=0)

        self.lb_file_list = tk.Listbox(self, height=20, selectmode=tk.EXTENDED)
        self.lb_file_list.grid(column=0, row=1, columnspan=3, sticky="ew", padx=8, pady=2)

        self.bt_flatten = tk.Button(self, text="Flatten", command=self.do_flatten)
        self.bt_flatten.grid(column=0, row=2)

        self.bt_flatten = tk.Button(self, text="Convert", command=self.do_convert)
        self.bt_flatten.grid(column=1, row=2)

        self.dd_var = tk.StringVar()
        self.dd_var.set(supported_filetypes[0])

        self.dd_filetypes = tk.OptionMenu(self, self.dd_var, *supported_filetypes, command=self.onselect)
        self.dd_filetypes.grid(column=2, row=2)


    def onselect(self, *args):
        pass


    def open_file(self, *args):
        self.file_list += tkinter.filedialog.askopenfilenames()
        self.lb_file_list.delete(0,tk.END)

        for item in self.file_list:
            self.lb_file_list.insert(tk.END, ntpath.basename(item))

    def do_flatten(self, *args):
        run = True
        for file in self.file_list:
            if ".pdf" not in file:
                run = False
                messagebox.showerror("Check files!", "Flatten only supports PDF files, please remove other filetypes.")
                break
        
        if run:
            for file in self.file_list:
                threadRun(flatten, file)
                #self.remove_item(file)

    def do_convert(self, *args):
        run = True
        # FILE CHECK GOES HERE
        
        if run:
            for file in self.file_list:
                threadRun(convert, file, self.dd_var.get())
                #self.remove_item(file)



    def remove_item(self, *args):
        selection = self.lb_file_list.curselection()
        for item in selection:
            self.file_list.pop(item)

        self.lb_file_list.delete(0, tk.END)
        for item in self.file_list:
            self.lb_file_list.insert(tk.END, ntpath.basename(item))


    def clear_all(self, *args):
        self.lb_file_list.delete(0,tk.END)
        self.file_list.clear()


root = tk.Tk()
root.title("loffPDF")
root.minsize(600, 680)
root.resizable(False, False)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

app = App(root)
app.grid(column=0, row=0, sticky="nsew", padx=4, pady=4)

root.mainloop()
 