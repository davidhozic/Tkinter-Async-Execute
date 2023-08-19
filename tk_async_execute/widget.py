"""
Async execution window.

--------------

MIT License

Copyright (c) 2023 David Hozic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from typing import Coroutine, Callable, Optional
from threading import current_thread

from tkinter import ttk
import tkinter as tk
from tkinter import messagebox

import asyncio
import sys

from . import doc


@doc.doc_category("Widgets")
class ExecutingAsyncWindow(tk.Toplevel):
    """
    Window that hovers while executing async methods.

    .. note::

        Direct usage of this is not recommended. Use :func:`tk_async_execute.async_execute` instead.

    Parameters
    -----------
    coro: Coroutine
        The coro to run.
    visible: Optional[bool]
        Show the execution progress through a new window.
        Defaults to True.
    pop_up: Optional[bool]
        If True, all other windows will be blocked from interactions, until the execution of ``coro`` is complete.
        Defaults to False.
    callback: Optional[Callable]
        Callback function to call with result afer coro has finished.
        Defaults to None.
    args: Any
        Other positional arguments passed to :class:`tkinter.Toplevel`
    kwargs: Any
        Other keyword arguments passed to :class:`tkinter.Toplevel`

    Raises
    ---------
    RuntimeError
        Loop has not been started, use 'tk_async_execute.start()' first.
    """
    loop: asyncio.AbstractEventLoop = None

    def __init__(
        self,
        coro: Coroutine,
        visible: bool = True,
        pop_up: bool = False,
        callback: Optional[Callable] = None,
        *args,
        **kwargs
    ):
        loop = self.loop
        if loop is None or not loop.is_running():
            raise RuntimeError("Start the loop first with 'tk_async_execute.start()'")

        super().__init__(*args, **kwargs)
        self.title("Async execution window")
        self.resizable(False, False)
        frame_main = ttk.Frame(self, padding=(10, 10))
        frame_main.pack(fill=tk.BOTH, expand=True)

        frame_stdout = ttk.Frame(frame_main)
        frame_stdout.pack(fill=tk.BOTH, expand=True)
        self.status_var = tk.StringVar()
        ttk.Label(frame_stdout, text="Last status: ").grid(row=0, column=0)
        ttk.Label(frame_stdout, textvariable=self.status_var).grid(row=0, column=1)

        ttk.Label(frame_main, text=f"Executing {coro.__name__}").pack(fill=tk.X)
        gauge = ttk.Progressbar(frame_main)
        gauge.start()
        gauge.pack(fill=tk.BOTH)
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        if not visible:
            self.withdraw()

        if pop_up:
            self.grab_set()

        self.awaitable = coro
        self.callback = callback
        self.current_thread = current_thread()

        self.old_stdout = sys.stdout
        sys.stdout = self

        self.future = future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.add_done_callback(lambda fut: self.after_idle(self.destroy, fut))

    def flush(self):
        pass

    def write(self, text: str):
        if current_thread() is not self.current_thread:  # Tkinter thread safety
            self.after_idle(self.write, text)
            return

        if text != "\n":
            self.status_var.set(text)
        
        self.old_stdout.write(text)

    def destroy(self, future: asyncio.Future = None) -> None:
        if future is not None and (exc := future.exception()) is not None:
            messagebox.showerror(
                "Coroutine error",
                f"{exc}\n(Error while running coroutine: {self.awaitable.__name__})\nType: {exc.__class__}",
                master=self
            )

        sys.stdout = self.old_stdout

        if self.callback is not None:
            self.callback()

        return super().destroy()
