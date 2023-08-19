# Tkinter-Async-Execute
Library provides a simple way to run an ``asyncio`` event loop alongside Tkinter, an ability to
run async functions (coroutines) directly from Tkinter callbacks and an optional async execution window, which
shows stdout on the screen.

# Example
```py
from tkinter import ttk
import tkinter as tk
import asyncio

import tk_async_execute as tk_async


async def async_function():
    print("Example")
    await asyncio.sleep(2)
    print("Done executing")
    await asyncio.sleep(1)


def button_clicked():
    # Call the async function
    tk_async.async_execute(async_function(), wait=True, visible=True, pop_up=True, callback=None, master=root)

    # Close application
    root.quit()


root = tk.Tk()
ttk.Button(root, text="Click me", command=button_clicked).pack()

tk_async.start()  # Starts the asyncio event loop in a different thread.
root.mainloop()  # Main Tkinter loop
tk_async.stop()  # Stops the event loop and closes it.
```