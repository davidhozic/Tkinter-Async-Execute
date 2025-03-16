========================
Changelog
========================
.. |BREAK_CH| replace:: **[Breaking change]**

.. |POTENT_BREAK_CH| replace:: **[Potentially breaking change]**

.. |UNRELEASED| replace:: **[Not yet released]**

------------------------
Info
------------------------

.. seealso:: 
    `Releases <https://github.com/davidhozic/Tkinter-Async-Execute/releases>`_  


Glossary
======================
.. glossary::

    |BREAK_CH|
        Means that the change will break functionality from previous version.

    |POTENT_BREAK_CH|
        The change could break functionality from previous versions but only if it
        was used in a certain way.

    |UNRELEASED|
        Documented changes are not yet available to use.


---------------------
Releases
---------------------

v1.4.0
==================
- Added extra parameters: ``window_title``, ``window_resizable``, ``stdout_labe_prefix``, ``show_progress_bar``.


v1.3.2
==================
- Fixed ``AttributeError: 'NoneType' object has no attribute 'write'`` exception when using PyInstaller with
  ``--noconsole`` option.


v1.3.1
==================
- Fixed *_tkinter.TclError: grab failed: window not viewable* error when ``pop_up`` was set to ``True``.


v1.3.0
==================
- Added ``message`` parameter to :func:`~tk_async_execute.utils.async_execute()` and
  :class:`~tk_async_execute.widget.ExecutingAsyncWindow` for displaying a custom message.
- Added ``show_stdout`` parameter to :func:`~tk_async_execute.utils.async_execute()` and
  :class:`~tk_async_execute.widget.ExecutingAsyncWindow` for toggling whether to show ``print()``
  messages inside the window.


v1.2.0
===========
- Added ``show_exceptions`` parameter to :func:`~tk_async_execute.utils.async_execute()` and
  :class:`~tk_async_execute.widget.ExecutingAsyncWindow`.
- Added :py:attr:`~tk_async_execute.widget.ExecutingAsyncWindow.future`


v1.1.0
=================
- Instead of showing a coroutine exception on screen when using
  :func:`~tk_async_execute.utils.async_execute()`, raise the exception.


v1.0.1
=================
- Fix event loop problems on Python before 3.10 due to semaphores (etc.) calling ``get_event_loop`` inside.


v1.0.0
=================
- Initial release
