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
from typing import Coroutine, Callable, Optional, Union, Tuple
from threading import current_thread
from concurrent.futures import Future

from tkinter import ttk
import tkinter as tk
from tkinter import messagebox

import asyncio
import sys

from . import doc


@doc.doc_category("Widgets", members=True)
class ExecutingAsyncWindow(tk.Toplevel):
    """
    Window that hovers while executing async methods.

    .. versionchanged:: v1.2

        - Removed ``*args`` parameter.
        - Added ``show_exceptions`` parameter.

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
        Callback function to call with result after coro has finished.
        Defaults to None.
    show_exceptions: Optional[bool]
        If True, any exceptions that ocurred in ``coro`` will be display though a message box on screen.
        If you want to obtain the exception though code, you can do so, by awaiting ``await Window.future`` and then
        read the exception with Window.future.exception() function.
    message: Optional[str | Callable[[str], str]]
        Message to be displayed in the window, when ``visible`` parameter is set to True.
        When a string (``str``) is provided, it will be displayed as the message.
        If a callable is provided, it will be called with the function name as a parameter,
        and it must return a string that will be used as the displayed message.
    show_stdout: Optional[bool]
        If True, any write to stdout (e.g., the ``print()`` function) will be displayed in the window when
        the execution window is shown (``visible=True``).
        Defaults to True.
    window_title: Optional[str]
        The title of this window. Defaults to "Async execution window".
    window_resizable: Optional[tuple[bool, bool]]
        Controls whether the window is resizable. The first component of this tuple represents
        the resizable-in-width and second resizable-in-height.
        Defaults to (False, False), meaning the window is not resizable in any direction.
    stdout_label_prefix: Optional[str],
        Only has an effect if the `show_stdout` parameter is set to `True`.
        Each time a message is printed via stdout, the window will show it.
        This parameter controls the text that is added in front of all messages.
        Defaults to "Last status: ".
    show_progress_bar: Opional[bool],
        Whether to show the progress bar (gauge). Note that this is only a free-running progress bar
        and it is meant to have a visual effect. It doesn't allow actual progress to be displayed.
        Defaults to `True`.
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
        show_exceptions: bool = True,
        message: Optional[Union[str, Callable[[str], str]]] = lambda name: f"Executing {name}",
        show_stdout: bool = True,
        # Tkinter-specific parameters
        window_title: str = "Async execution window",
        window_resizable: Tuple[bool, bool] = (True, False),
        stdout_label_prefix: str = "Last status: ",
        show_progress_bar: bool = True,
        **kwargs
    ):
        loop = self.loop
        if loop is None or not loop.is_running():
            raise RuntimeError("Start the loop first with 'tk_async_execute.start()'")

        super().__init__(**kwargs)
        self.show_exceptions = show_exceptions
        self.title(window_title)
        self.resizable(*window_resizable)
        frame_main = ttk.Frame(self, padding=(10, 10))
        frame_main.pack(fill=tk.BOTH, expand=True)

        frame_stdout = ttk.Frame(frame_main)
        frame_stdout.pack(fill=tk.BOTH, expand=True)
        self.status_var = tk.StringVar()
        self.current_thread = current_thread()
        self.old_stdout = sys.stdout
        if show_stdout:
            sys.stdout = self
            ttk.Label(frame_stdout, text=stdout_label_prefix).grid(row=0, column=0)
            ttk.Label(frame_stdout, textvariable=self.status_var).grid(row=0, column=1)

        if callable(message):
            message = message(coro.__name__)

        ttk.Label(frame_main, text=message).pack(fill=tk.X)
        if show_progress_bar:
            self.gauge = ttk.Progressbar(frame_main)
            self.gauge.pack(fill=tk.BOTH)
            self.gauge.start()
        else:
            self.gauge = None

        self.protocol("WM_DELETE_WINDOW", lambda: None)

        if not visible:
            self.withdraw()

        if pop_up:
            self.wait_visibility()
            self.grab_set()

        self.awaitable = coro
        self.callback = callback

        self._future = future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.add_done_callback(lambda fut: self.after_idle(self.destroy, future))

    @property
    def future(self) -> Future:
        """
        Returns concurrent.futures.Future object.
        This can be used to eg. obtain the coroutine result (``future.result()``)
        or the exception (``future.exception()``).
        """
        return self._future

    def flush(self):
        pass

    def write(self, text: str):
        if current_thread() is not self.current_thread:  # Tkinter thread safety
            self.after_idle(self.write, text)
            return

        if text != "\n":
            self.status_var.set(text)
        
        # Original sys.stdout can be None when using programs such as pyinstaller (with --noconsole option).
        if self.old_stdout is not None:
            self.old_stdout.write(text)

    def destroy(self, future: asyncio.Future = None) -> None:
        if future is not None and (exc := future.exception()) is not None and self.show_exceptions:
            # ttkbootstrap compatibility
            title = f"{self.awaitable.__name__} error"
            message = f"{exc}\n\n({type(exc).__name__})"
            if "ttkbootstrap" in sys.modules:
                from ttkbootstrap.dialogs.dialogs import Messagebox
                Messagebox.show_error(message, title, self.master)
            else:
                Messagebox = messagebox.showerror(title, message, master=self.master)

        sys.stdout = self.old_stdout

        if self.callback is not None:
            self.callback()

        return super().destroy()
