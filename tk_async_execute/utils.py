"""
Asyncio event loop utilities.

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

from typing import Coroutine, Optional, Callable, Union
from threading import Thread
from concurrent.futures import Future as TFuture

import asyncio
import sys

from .widget import ExecutingAsyncWindow
from . import doc


class GLOBAL:
    async_thread: Thread = None
    loop: asyncio.AbstractEventLoop = None


@doc.doc_category("Control")
def stop():
    """
    Stops the async queue executor.

    This should be called from tkinter callbacks, not from async functions.   
    """
    if GLOBAL.async_thread is None or not GLOBAL.async_thread.is_alive():
        return  # Not running, skip

    loop = GLOBAL.loop
    loop.call_soon_threadsafe(loop.stop)
    GLOBAL.async_thread.join()
    asyncio.set_event_loop(None)
    loop.close()
    ExecutingAsyncWindow.loop = None
    return loop


@doc.doc_category("Control")
def start():
    """
    Starts the async queue executor.

    Raises
    ---------
    RuntimeError
        The loop is already running. Stop it with ``tk_async_execute.stop()`` first.
    """
    if GLOBAL.async_thread is not None and GLOBAL.async_thread.is_alive():
        raise RuntimeError("Event loop already started. Stop it with ``tk_async_execute.stop()`` first")

    # Semaphores, etc on version prior to 3.10, call get_event_loop inside, which will cause
    # exceptions if new_event_loop is created and started.
    if sys.version_info.minor < 10:
        loop = asyncio.get_event_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    GLOBAL.loop = loop
    GLOBAL.async_thread = Thread(target=loop.run_forever)
    ExecutingAsyncWindow.loop = loop
    GLOBAL.async_thread.start()


@doc.doc_category("Execution")
def tk_execute(method: Callable, *args, **kwargs):
    """
    Allows thread-safe execution of tkinter methods.

    Parameters
    -----------
    method: Callable
        A **tkinter widget** method.
        Methods that are not from tkinter widgets,
        should be called directly without this function.
    args: Any
        Positional arguments to pass to ``method``
    kwargs: Any
        Keyword arguments to pass to ``method``
    """
    widget = method.__self__
    future = TFuture()

    def safe_execute():
        future.set_result(method(*args, **kwargs))

    widget.after_idle(safe_execute)
    return future.result()


@doc.doc_category("Execution")
def async_execute(
    coro: Coroutine,
    wait: bool = True,
    visible: bool = True,
    pop_up: bool = False,
    callback: Optional[Callable] = None,
    show_exceptions: bool = True,
    message: Optional[Union[str, Callable[[str], str]]] = lambda name: f"Executing {name}",
    show_stdout: bool = True,
    **kwargs
):
    """
    Executes a coroutine inside asyncio event loop.
    
    Call this from tkinter callbacks.

    Parameters
    ---------------
    coro: Coroutine
        The coro to run.
    wait: Optional[bool]
        Wait until the execution of ``coro`` has completed, before returning from this function.
        Defaults to True.

        **WARNING** If multiple executions are happening at once, due to the way tkinter's event loop works, this will
        wait for all executions to finish before returning from this function in the LIFO manner
        (last execution will be exited first).

    visible: Optional[bool]
        Show the execution progress through a new window.
        Defaults to True.
    pop_up: Optional[bool]
        If True, all other windows will be blocked from interactions, until the execution of ``coro`` is complete.
        Defaults to False.
    callback: Optional[Callable]
        Callback function to call with result afer coro has finished.
        Defaults to None.
    show_exception: Optional[bool]
        If True, any exceptions that ocurred in ``coro`` will be display though a message box on screen.
        If you want to obtain the exception though code, you can do so by setting parameter ``wait`` of this function
        to True and then calling ``window.future.exception()``.
    message: Optional[str | Callable[[str], str]]
        Message to be displayed in the window, when ``visible`` parameter is set to True.
        When a string (``str``) is provided, it will be displayed as the message.
        If a callable is provided, it will be called with the function name as a parameter,
        and it must return a string that will be used as the displayed message.
    show_stdout: Optional[bool]
        If True, any write to stdout (e.g., the ``print()`` function) will be displayed in the window when
        the execution window is shown (``visible=True``).
        Defaults to True.
    **kwargs
        Any tkinter specific parameters to the TopLevel widget.

    Returns
    -----------
    ExecutingAsyncWindow
        The progress TopLevel window responsible for ``coro`` execution.

    Raises
    --------
    Exception
        Exception that occurred in ``coro`` (if it ocurred). Only raised if ``wait`` is True.
    """
    window = ExecutingAsyncWindow(coro, visible, pop_up, callback, show_exceptions, message, show_stdout, **kwargs)
    if wait:
        window.wait_window()

    return window
