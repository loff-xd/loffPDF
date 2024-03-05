from wand.image import Image
import threading
from pathlib import Path


# MAIN WORKER THREAD CONTROLLER
def threadRun(func, filetype, *args):
    thread = threading.Thread(target=func, args=(filetype,), daemon=True)
    thread.start()


# WORKER TASKS
def flatten(filePath, filetype, *options):
    with Image(filename=filePath) as src:
        with src.convert("pdf") as out:
            output = Path(filePath).stem + "_flattened.pdf"
            out.save(filename=output)

    print("Flatten done: " + filePath + " -> " + output)

def convert(filePath, filetype, *options):
    with Image(filename=filePath) as src:
        with src.convert(filetype.replace(".", "")) as out:
            output = Path(filePath).stem + "_converted" + filetype
            out.save(filename=output)

    print("Convert done: " + filePath + " -> " + output)


if __name__ == "__main__":
    # FOR TESTING ONLY
    filename = input("Enter filename: ")
    threadRun(flatten, filename)
