from gi.repository import GLib
from asyncio.locks import BoundedSemaphore


def from_main_thread_wait(callable, *args, **kwargs):
    s = BoundedSemaphore(0)
    def complete(callable, *args, **kwargs):
        callable(*args, **kwargs)
        s.release()
    GLib.idle_add(complete, callable, *args, **kwargs)
    s.acquire()

def from_main_thread_callback(callable):
    def f(*args, **kwargs):
        GLib.idle_add(callable, *args, **kwargs)
    return f
