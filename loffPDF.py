import tkinter as tk
import tkinter.filedialog
import ntpath

from backend import *


class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.file_list = []

        self.bt_open = tk.Button(self, text="Open", command=self.open_file)
        self.bt_open.grid(column=0, row=0)

        self.lb_file_list = tk.Listbox(self, height=10)
        self.lb_file_list.grid(column=0, row=1, sticky="ew")

        self.bt_flatten = tk.Button(self, text="Flatten", command=self.do_flatten)
        self.bt_flatten.grid(column=0, row=2)


    def open_file(self, *args):
        self.file_list = tkinter.filedialog.askopenfilenames()
        print(self.file_list)

        for item in self.file_list:
            self.lb_file_list.insert(tk.END, ntpath.basename(item))

    def do_flatten(self, *args):
        for file in self.file_list:
            threadRun(flatten, file)
        self.lb_file_list.delete(0, tk.END)



root = tk.Tk()
root.title("loffPDF")
root.minsize(300, 600)

app = App(root)
app.grid(column=0, row=0, sticky="nsew")

root.mainloop()
