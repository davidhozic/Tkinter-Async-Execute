# Tkinter-Async-Execute
Library provides a simple way to run an ``asyncio`` event loop alongside Tkinter, an ability to
run async functions (coroutines) directly from Tkinter callbacks and an optional async execution window, which
shows stdout on the screen. Additionally it provides a `tk_execute` function that allows execution of tkinter methods
from different threads or async functions in a thread-safe way.

# Example
```py
from tkinter import ttk
import tkinter as tk
import asyncio

import tk_async_execute as tk_async


async def async_function():
    print("Example")  # Shown in the window
    await asyncio.sleep(2)

    # Call tkinter widget methods.
    print("Disabling button")
    tk_async.tk_execute(bnt.config, state="disabled")  # Thread safe exection
    await asyncio.sleep(5)
    print("Enabling button")
    tk_async.tk_execute(bnt.config, state="normal")
    await asyncio.sleep(2)

    # Change tkinter text
    print("Renaming button")
    tk_async.tk_execute(bnt.config, text="Example 2")
    await asyncio.sleep(2)


def button_clicked():
    # Call async function
    tk_async.async_execute(async_function(), wait=True, visible=True, pop_up=True, callback=None, master=root)

    # Close application
    root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    bnt = ttk.Button(root, text="Click me", command=button_clicked, width=20)
    bnt.pack()

    tk_async.start()  # Starts the asyncio event loop in a different thread.
    root.mainloop()  # Main Tkinter loop
    tk_async.stop()  # Stops the event loop and closes it.
```