from wand.image import Image
import threading
import time


# MAIN WORKER THREAD CONTROLLER
def threadRun(func, *args):
    thread = threading.Thread(target=func, args=args)
    thread.start()

    print("Worker started")
    while thread.is_alive():
        print(".", end="", flush=True)
        time.sleep(0.5)
    print("Worker done")

# WORKER TASKS
def flatten(filePath, *options):
    with Image(filename=filePath) as src:
        with src.convert("pdf") as out:
            out.save(filename="out.pdf")


if __name__ == "__main__":
    filename = input("Enter filename:")
    threadRun(flatten, filename)
