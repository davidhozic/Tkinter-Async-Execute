======================
Tkinter-Async-Execute
======================

Tkinter-Async-Execute is a small library, that provides a way to run an ``asyncio`` event loop alongside Tkinter in
a separate thread.

It provides a way to execute methods of tkinter widgets from inside async functions and ability to call async functions
from functions (commands / events) running in tkinter's thread. The former can be called from any thread (or async function)
and the latter only from functions (commands / events) in tkinter's thread.

To show progress of an async function, submitted from tkinter, an async execution window widget is available,
which will display any text printed with the ``print()`` function (or any stdout write requests).


Installation
==============
.. code-block:: bash

    pip install tkinter-async-execute

Documentation
=============
All documentation is available on https://tkinter-async-execute.readthedocs.io/.


Example
=============
.. code-block:: python

    from tkinter import ttk
    import tkinter as tk
    import asyncio

    import tk_async_execute as tae


    async def async_function():
        # Call tkinter widget methods.
        print("Disabling button")
        tae.tk_execute(bnt.config, state="disabled")  # Thread safe exection
        await asyncio.sleep(5)
        print("Enabling button")
        tae.tk_execute(bnt.config, state="normal")
        await asyncio.sleep(2)

        # Change tkinter text
        print("Renaming button")
        tae.tk_execute(bnt.config, text="Example 2")
        await asyncio.sleep(2)


    def button_clicked():
        # Call async function
        tae.async_execute(async_function(), wait=True, visible=True, pop_up=True, callback=None, master=root)

        # Close application
        root.quit()


    if __name__ == "__main__":
        root = tk.Tk()
        bnt = ttk.Button(root, text="Click me", command=button_clicked, width=20)
        bnt.pack()

        tae.start()  # Starts the asyncio event loop in a different thread.
        root.mainloop()  # Main Tkinter loop
        tae.stop()  # Stops the event loop and closes it.
