__all__ = [
    "dedicated"
]


from multiprocessing import (
    Process,
    Queue
)
from threading import (
    Thread
)


RESERCED = set(["terminate", "fork"])


def dedicated(entity):
    """ Decorator for `pickle`-able class & its methods. A user calls `fork`
on an instance of a decorated class which creates a process with copy of the
instance. Then user calls a `dedicated` method on instance and it will be
actually executed in forked process and return value is fed back.
Both arguments and return value must be `pickle`-able.
Non-decorated methods are executed in context of calling process.
Operation is synchronous. A use case is to launch threads after `fork` using
`dedicated` methods, and the `dedicated` class has role of a thread manager.
If `dedicated` class has `main` attribute, it will be executed in main
thread of forked process.
That is intentionally designed to support GUI frameworks whose main loop can
only operate in main thread.
    """
    if isinstance(entity, type):
        backends = ["terminate"]
        for name, method in entity.__dict__.items():
            if name in RESERCED:
                raise TypeError(("`%s` attribute name is reserved for " +
                    "`dedicated` implementation") % name
                )
            if not hasattr(method, "_dedicated"):
                continue
            del method._dedicated
            backends.append(name)

        def fork(self):
            c2s, s2c = Queue(1), Queue(1)

            p = Process(target = starter, args = (self, c2s, s2c))
            p.start()

            for name in backends:
                setattr(self, name, gen_frontend(name, c2s, s2c))

        entity.fork = fork
    else: # it's a method in class
        entity._dedicated = True

    return entity


def gen_frontend(name, c2s, s2c):

    def frontend(*a, **kw):
        c2s.put((name, a, kw))
        exc, ret = s2c.get()
        if exc:
            raise ret
        else:
            return ret

    return frontend


def dispatch_loop(entity, c2s, s2c):
    while True:
        name, a, kw = c2s.get()
        if name == "terminate":
            s2c.put((False, None))
            break
        try:
            ret = getattr(entity, name)(*a, **kw)
        except BaseException as e:
            s2c.put((True, e))
        else:
            s2c.put((False, ret))


def starter(entity, c2s, s2c):
    if hasattr(entity, "main"):
        # We must run `main` in main thread. Start new thread for dispatcher.
        dispatch_thread = Thread(
            name = "dispatcher",
            target = dispatch_loop,
            args = (entity, c2s, s2c)
        )
        dispatch_thread.start()

        entity.main()

        # Without this `join` the `frontend` of `terminate` does not `get`
        # `None` sent by `dispatch_loop` and freezes. Probably, because this
        # main thread finishes.
        dispatch_thread.join()
    else:
        # No function for main thread. We can use main thread for dispatcher.
        dispatch_loop(entity, c2s, s2c)
