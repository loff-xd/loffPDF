from wand.image import Image
import threading
from pathlib import Path


# MAIN WORKER THREAD CONTROLLER
def threadRun(func, *args):
    thread = threading.Thread(target=func, args=args, daemon=True)
    print("Worker starting")
    thread.start()


# WORKER TASKS
def flatten(filePath, *options):
    with Image(filename=filePath) as src:
        with src.convert("pdf") as out:
            output = Path(filePath).stem + "_flattened.pdf"
            out.save(filename=output)

    print("Flatten done: " + filePath + " -> " + output)


if __name__ == "__main__":
    # FOR TESTING ONLY
    filename = input("Enter filename: ")
    threadRun(flatten, filename)
