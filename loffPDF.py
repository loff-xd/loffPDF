import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
from tkinter import messagebox
import ntpath
from wand.image import Image
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from PIL import Image as PILImage
import pillow_heif

supported_savetypes = [
    ".pdf",
    ".jpg",
    ".png"
]

supported_filetypes = [
    ".pdf",
    ".jpg",
    ".png",
    ".heic",
    "tiff",
    "bmp"
]

status_out = ""

# MULTIPROCESSING
exe = ProcessPoolExecutor()
futures = []


class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.file_list = []

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=0)

        self.bt_open = ttk.Button(self, text="Open/Add", command=self.open_file)
        self.bt_open.grid(column=0, row=0)
        self.bt_open.bind("<Shift-Button-1>", self.force_open_file)

        self.bt_remove = ttk.Button(self, text="Remove", command=self.remove_item)
        self.bt_remove.grid(column=1, row=0)

        self.bt_remove = ttk.Button(self, text="Clear", command=self.clear_all)
        self.bt_remove.grid(column=2, row=0)

        self.lb_file_list = tk.Listbox(self, height=20, selectmode=tk.EXTENDED)
        self.lb_file_list.grid(column=0, row=1, columnspan=3, sticky="ew", padx=8, pady=8)

        self.bt_flatten = ttk.Button(self, text="Flatten/Fix PDFs", command=self.do_flatten)
        self.bt_flatten.grid(column=0, row=2)

        self.bt_convert = ttk.Button(self, text="Convert to new format:", command=self.do_convert)
        self.bt_convert.grid(column=1, row=2)

        self.dd_var = tk.StringVar()
        self.dd_var.set(supported_savetypes[0])

        self.dd_filetypes = ttk.OptionMenu(self, self.dd_var, *supported_savetypes)
        self.dd_filetypes.grid(column=2, row=2)

        self.tx_output = tk.Text(self, height=8)
        self.tx_output.grid(column=0, row=4, columnspan=3, sticky="nsew", padx=8, pady=8)
        self.tx_output.insert(1.0, "Ready.")
        self.tx_output.config(state="disabled")

        self.pb_progress = ttk.Progressbar()
        self.pb_progress.grid(column=0, row=3, columnspan=3, sticky="ew", padx=8, pady=8)


    def open_file(self, force=False, *args):
        if not force:
            types = []
            for type in supported_filetypes:
                types.append(("", type))
            self.file_list += tkinter.filedialog.askopenfilenames(filetypes=types)
        else:
            self.file_list += tkinter.filedialog.askopenfilenames()

        self.lb_file_list.delete(0,tk.END)

        for item in self.file_list:
            self.lb_file_list.insert(tk.END, ntpath.basename(item))

    def force_open_file(self, *args):
        self.open_file(True)

    def do_flatten(self, *args):
        if len(self.file_list) != 0:
            self.output_write("", clear=True)
            self.output_write("Flattening " + str(len(self.file_list)) + " files")

            run = True
            for file in self.file_list:
                if ".pdf" not in file:
                    run = False
                    messagebox.showerror("Check files!", "Flatten only supports PDF files, please remove other filetypes.")
                    break
            
            if run:
                for file in self.file_list:
                    future = exe.submit(flatten, file)
                    future.add_done_callback(self.task_callback)
                    futures.append(future)

                self.lb_file_list.delete(0,tk.END)
                self.file_list.clear()
                self.bt_flatten.config(state="disabled")
                self.bt_convert.config(state="disabled")
                self.pb_progress.config(mode="indeterminate")
                self.pb_progress.start()

    def do_convert(self, *args):
        if len(self.file_list) != 0:
            self.output_write("", clear=True)
            self.output_write("Converting " + str(len(self.file_list)) + " files")


            for file in self.file_list:
                    future = exe.submit(convert, file, self.dd_var.get())
                    future.add_done_callback(self.task_callback)
                    futures.append(future)

            self.lb_file_list.delete(0,tk.END)
            self.file_list.clear()
            self.bt_convert.config(state="disabled")
            self.bt_flatten.config(state="disabled")
            self.pb_progress.config(mode="indeterminate")
            self.pb_progress.start()

    def reset_gui(self):
        self.bt_flatten.config(state="normal")
        self.bt_convert.config(state="normal")
        self.pb_progress.config(mode="determinate")
        self.pb_progress.stop()
        self.pb_progress.step(99.9)

    def task_callback(self, future):
        if future.exception() is None:
            self.output_write(future.result())
            if all(task.done() for task in futures):
                futures.clear()
                self.output_write("Complete.")
                self.reset_gui()
            else:
                self.pb_progress.config(mode="determinate")
                self.pb_progress.stop()
                self.pb_progress.step((sum(task.done() for task in futures) / len(futures)) * 99.9)
        else:
            self.output_write("An error occured")

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
        self.output_write("", clear=True)

    def output_write(self, text, clear=False):
        self.tx_output.config(state="normal")
        if clear:
            self.tx_output.delete(1.0, tk.END)
        else:
            self.tx_output.insert(tk.END, text + "\n")
        self.tx_output.config(state="disabled")



# WORKER TASKS
def flatten(file, *options):
    with Image(filename=file) as src:
        with src.convert("pdf") as out:
            output = Path(file).stem + "_flattened.pdf"
            out.save(filename=output)

    return "Flattened: " + output

def convert(file, filetype, *options):
        if Path(file).suffix != ".heic":
            with Image(filename=file) as src:
                with src.convert(filetype.replace(".", "")) as out:
                    output = Path(file).stem + "_converted" + filetype
                    out.save(filename=output)
        else:
            raw = pillow_heif.read_heif(file)
            src = PILImage.frombytes(raw.mode,
                raw.size,
                raw.data,
                "raw",)
            output = Path(file).stem + "_converted" + filetype
            if filetype == ".jpg":
                src.convert("RGB").save(output)
            else:
                src.save(output)

        return "Converted: " + output

# MAIN APP

root = tk.Tk()
root.title("loffPDF")
root.minsize(600, 400)
root.resizable(False, False)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

app = App(root)
app.grid(column=0, row=0, sticky="nsew", padx=4, pady=4)

root.mainloop()
